# Настройка поддоменов через админку Saleor

Частично функциональность для поддоменов можно настроить через стандартную админку Saleor Dashboard, но для полноценного решения потребуются дополнительные разработки.

## Что можно настроить через админку:

1. **Каналы (Channels)** - можно создать отдельный канал для каждого поддомена:
   - В Saleor Dashboard перейдите в раздел "Channels"
   - Создайте новый канал для каждого поддомена (например, "moscow", "spb")
   - Настройте для каждого канала валюту и параметры доставки

2. **Цены для разных каналов**:
   - В карточке товара перейдите в раздел "Pricing"
   - Там можно установить разные цены для каждого канала

## Что нельзя настроить через стандартную админку:

1. **Привязку поддоменов к каналам** - стандартный Saleor не имеет интерфейса для назначения поддоменов определенным каналам

2. **DNS и веб-сервер** - настройка поддоменов на уровне сервера делается вне Saleor

## Варианты решения:

1. **Расширение Dashboard через Saleor App**:
   - Создайте приложение для Saleor с пользовательским интерфейсом
   - Добавьте в него функциональность управления поддоменами

2. **Использование метаполей**:
   - К каналам можно добавить метаданные через API, которые будут хранить информацию о поддомене:

   ```python
   # Пример добавления метаданных через API
   channel = Channel.objects.get(slug="moscow")
   channel.metadata = {"subdomain": "moscow"}
   channel.save()
   ```

   Затем в админке можно через API управлять этими метаданными.

3. **Простая таблица соответствий**:
   - Для небольшого количества поддоменов можно использовать простую конфигурацию в коде или файле настроек.

В любом случае, для полноценной работы системы поддоменов с разными ценами потребуется дополнительная разработка поверх базового Saleor, так как это не входит в стандартную функциональность платформы.

---

# Реализация процентных добавок к базовой цене для разных каналов в Saleor

Для реализации логики с процентными добавками к базовой цене товара для разных каналов можно использовать несколько подходов:

## 1. Через метаданные каналов

```python
# Сохраняем процентную надбавку в метаданных канала
from saleor.channel.models import Channel

channel = Channel.objects.get(slug="moscow")
channel.metadata = {"price_markup_percent": "15"}  # 15% наценка для московского канала
channel.save()

channel = Channel.objects.get(slug="spb") 
channel.metadata = {"price_markup_percent": "10"}  # 10% наценка для СПб
channel.save()
```

## 2. Создание middleware для автоматического расчета цен

```python
# middleware.py
class PriceMarkupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        # Проверяем, что мы работаем с API, возвращающим товары
        if hasattr(response, 'data') and 'products' in response.data:
            channel = request.channel
            
            if channel and channel.metadata.get('price_markup_percent'):
                markup = float(channel.metadata.get('price_markup_percent')) / 100
                
                # Применяем наценку ко всем товарам в ответе
                for product in response.data['products']:
                    if 'price' in product:
                        base_price = product['price']['amount']
                        product['price']['amount'] = base_price * (1 + markup)
                        
        return response
```

## 3. Модификация сервиса цен (более профессиональный подход)

```python
# price_service.py
from decimal import Decimal
from saleor.product.models import ProductVariantChannelListing

class PriceService:
    @staticmethod
    def get_price_with_markup(variant_id, channel_id):
        # Получаем базовую цену
        variant_channel = ProductVariantChannelListing.objects.get(
            variant_id=variant_id,
            channel_id=channel_id
        )
        base_price = variant_channel.price_amount
        
        # Получаем наценку из метаданных канала
        channel = variant_channel.channel
        markup_percent = Decimal(channel.metadata.get('price_markup_percent', '0'))
        markup_multiplier = Decimal('1') + (markup_percent / Decimal('100'))
        
        # Применяем наценку
        final_price = base_price * markup_multiplier
        
        return final_price.quantize(Decimal('0.01'))  # Округляем до копеек
```

## 4. Расширение GraphQL API для работы с наценками

```python
# schema.py
import graphene
from decimal import Decimal
from saleor.graphql.core.types import BaseObjectType
from saleor.channel.models import Channel

class ChannelPriceMarkupInput(graphene.InputObjectType):
    channel_id = graphene.ID(required=True)
    markup_percent = graphene.Decimal(required=True)

class SetChannelPriceMarkup(graphene.Mutation):
    class Arguments:
        input = ChannelPriceMarkupInput(required=True)
    
    success = graphene.Boolean()
    
    @classmethod
    def mutate(cls, root, info, input):
        # Проверка прав доступа
        if not info.context.user.has_perm("channel.manage_channels"):
            raise PermissionDenied()
        
        channel_id = input["channel_id"]
        markup = input["markup_percent"]
        
        # Валидация значения наценки
        if markup < Decimal('0'):
            raise ValidationError("Наценка не может быть отрицательной")
        
        channel = Channel.objects.get(pk=channel_id)
        channel.metadata = {**channel.metadata, "price_markup_percent": str(markup)}
        channel.save(update_fields=["metadata"])
        
        return SetChannelPriceMarkup(success=True)
```

## 5. Создание интерфейса в админке

Для удобства настройки наценок в админке можно создать расширение через Saleor App:

```javascript
// frontend.jsx
import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_CHANNELS, SET_CHANNEL_MARKUP } from './queries';

const PriceMarkupManager = () => {
  const { data, loading } = useQuery(GET_CHANNELS);
  const [setMarkup] = useMutation(SET_CHANNEL_MARKUP);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>Управление наценками по каналам</h2>
      {data.channels.map(channel => (
        <div key={channel.id}>
          <h3>{channel.name}</h3>
          <input 
            type="number" 
            defaultValue={channel.metadata.price_markup_percent || 0}
            onChange={(e) => {
              setMarkup({ 
                variables: { 
                  input: {
                    channelId: channel.id,
                    markupPercent: parseFloat(e.target.value)
                  }
                }
              });
            }}
          />%
        </div>
      ))}
    </div>
  );
};
```

Этот подход позволит хранить базовую цену товара, а для каждого канала применять индивидуальную процентную надбавку, что значительно упростит управление ценами в мультиканальной системе.

---

# Интеграция кода в структуру Saleor

Предложенные мною фрагменты кода интегрируются в разные части Saleor следующим образом:

1. **Метаданные каналов** (первый пример) - это код для одноразового запуска через Django shell или скрипт миграции данных:
   ```bash
   python manage.py shell
   # Затем вставляете код для установки метаданных каналов
   ```

2. **Middleware** (второй пример) нужно добавить в:
   - Создайте файл `middleware.py` в вашем Django-приложении
   - Зарегистрируйте его в `settings.py` в списке `MIDDLEWARE`
   ```python
   MIDDLEWARE = [
       # ... другие middleware
       'your_app.middleware.PriceMarkupMiddleware',
       # ...
   ]
   ```

3. **Сервис цен** (третий пример) следует поместить в:
   - Создайте файл `services/price_service.py` в вашем приложении
   - Используйте его в ваших представлениях или API-обработчиках

4. **Расширение GraphQL API** (четвертый пример):
   - Добавьте код в `graphql/channel/mutations.py` вашего приложения
   - Зарегистрируйте новую мутацию в корневой схеме GraphQL

5. **Интерфейс в админке** (пятый пример):
   - Создайте Saleor App (отдельное приложение)
   - В структуре этого приложения создайте React-компонент
   - Подключите его через Saleor App SDK в дашборд

Для полной интеграции вам потребуется создать отдельное Django-приложение внутри вашей инсталляции Saleor или разработать расширение (Saleor App), которое будет взаимодействовать с API Saleor.

Если вы разрабатываете внутреннее приложение, структура может быть такой:
```
your_saleor_instance/
  ├── apps/
  │    └── price_manager/
  │         ├── __init__.py
  │         ├── apps.py
  │         ├── middleware.py
  │         ├── services/
  │         │    └── price_service.py
  │         ├── graphql/
  │         │    └── schema.py
  │         └── migrations/
  └── saleor/
       └── settings.py  # Здесь регистрируются middleware и приложения
```

---

# Использование FastAPI вместо Django для интеграции с Saleor

Вы абсолютно можете использовать FastAPI вместо встраивания кода непосредственно в Django. Это даже предпочтительнее в современной архитектуре Saleor, так как позволяет создать отдельное микросервисное приложение (Saleor App).

## Преимущества использования FastAPI:

1. **Независимость от кодовой базы Saleor** - не нужно модифицировать основной код Saleor
2. **Проще обновлять Saleor** - ваши расширения не ломаются при обновлении платформы
3. **Лучшая изоляция** - ошибки в вашем коде не влияют на работу основной платформы
4. **Современный стек** - асинхронность, типизация и высокая производительность FastAPI

## Пример структуры FastAPI приложения для Saleor:

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import requests
import json
from decimal import Decimal

app = FastAPI(title="Saleor Price Markup Service")

class ChannelMarkup(BaseModel):
    channel_id: str
    markup_percent: float

@app.post("/set-markup/")
async def set_channel_markup(markup: ChannelMarkup, token: str = Depends(get_token)):
    """Устанавливает процентную наценку для канала"""
    # Делаем API-запрос к Saleor, чтобы обновить метаданные канала
    headers = {"Authorization": f"Bearer {token}"}
    mutation = """
    mutation UpdateChannelMetadata($id: ID!, $input: [MetadataInput!]!) {
      updateMetadata(id: $id, input: $input) {
        item {
          metadata {
            key
            value
          }
        }
        errors {
          field
          message
        }
      }
    }
    """
    variables = {
        "id": markup.channel_id,
        "input": [{"key": "price_markup_percent", "value": str(markup.markup_percent)}]
    }
    
    response = requests.post(
        "https://your-saleor-instance/graphql/",
        json={"query": mutation, "variables": variables},
        headers=headers
    )
    
    data = response.json()
    if "errors" in data or (data.get("data", {}).get("updateMetadata", {}).get("errors")):
        raise HTTPException(status_code=400, detail="Failed to update channel markup")
    
    return {"success": True}

@app.get("/calculate-price/")
async def calculate_price(product_id: str, channel_slug: str):
    """Рассчитывает цену продукта с учетом наценки канала"""
    # Получаем базовую цену из Saleor
    base_price = get_product_base_price(product_id, channel_slug)
    
    # Получаем наценку для канала
    markup_percent = get_channel_markup(channel_slug)
    
    # Рассчитываем итоговую цену
    final_price = base_price * (1 + (markup_percent / 100))
    
    return {
        "product_id": product_id,
        "channel": channel_slug,
        "base_price": base_price,
        "markup_percent": markup_percent,
        "final_price": round(final_price, 2)
    }
```

## Интеграция с Saleor:

1. **API Webhook** - настройте в Saleor webhook, который будет вызывать ваш FastAPI сервис при изменении цен

2. **Saleor App** - разработайте официальное Saleor App, которое:
   - Регистрирует webhook для обработки событий Saleor
   - Предоставляет пользовательский интерфейс для настройки наценок
   - Взаимодействует с API Saleor для получения и обновления данных

```python
# saleor_app.py
from fastapi import FastAPI, Request, Response, BackgroundTasks
from pydantic import BaseModel
from saleor_app_sdk import SaleorApp

app = FastAPI()
saleor_app = SaleorApp(
    name="Price Markup Manager",
    webhook_url="https://your-fastapi-service.com/webhook"
)

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    event_data = await request.json()
    event_type = event_data.get("type")
    
    if event_type == "PRODUCT_UPDATED":
        # Обработка обновления продукта
        background_tasks.add_task(recalculate_prices, event_data["product"]["id"])
    
    return Response(status_code=200)
```

## Для фронтенда:

```javascript
// React компонент для управления наценками
import React, { useState, useEffect } from 'react';
import { useAppBridge } from '@saleor/app-sdk/app-bridge';
import { useQuery, useMutation } from '@apollo/client';

export const MarkupManager = () => {
  const { appBridgeState } = useAppBridge();
  const [channels, setChannels] = useState([]);
  
  useEffect(() => {
    // Загрузка списка каналов через Saleor API
    fetch('https://your-fastapi-service.com/channels')
      .then(res => res.json())
      .then(data => setChannels(data));
  }, []);
  
  return (
    <div>
      <h1>Управление наценками</h1>
      {channels.map(channel => (
        <ChannelMarkupForm 
          key={channel.id} 
          channel={channel} 
          token={appBridgeState.token}
        />
      ))}
    </div>
  );
};
```

Такой подход с использованием FastAPI будет более гибким, масштабируемым и соответствующим современной архитектуре Saleor, основанной на расширениях через Saleor Apps.

---

## Пример `.env` файла

```env
# URL вашего FastAPI сервера (локальный адрес для API)
APP_URL=http://localhost:8000

# URL фронтенд-приложения (локальный адрес для React)
APP_FRONTEND_URL=http://localhost:3000

# URL GraphQL API Saleor Cloud
SALEOR_API_URL=https://your-instance.saleor.cloud/graphql/

# Токен для авторизации в Saleor API
SALEOR_APP_TOKEN=your_saleor_app_token

# URL для подключения к Redis (локальный Redis или через Docker)
REDIS_URL=redis://localhost:6379/0

# Список разрешённых источников для CORS
CORS_ORIGINS=["https://your-instance.saleor.cloud", "http://localhost:3000"]
```

## Пояснения по заполнению

1. **APP_URL**
   - Укажите локальный адрес FastAPI сервера: `http://localhost:8000`.
   - Без ngrok Saleor Cloud не сможет отправлять вебхуки на ваш локальный сервер, так как `localhost` недоступен извне. Для тестирования API-запросов (например, через Postman или фронтенд) это подойдёт, но вебхуки потребуют ручной эмуляции (см. ниже).

2. **APP_FRONTEND_URL**
   - Укажите локальный адрес фронтенда: `http://localhost:3000` (по умолчанию для React).
   - Это позволит Saleor Dashboard загружать ваш фронтенд в iframe локально для тестирования интерфейса.

3. **SALEOR_API_URL**
   - Укажите URL вашего Saleor Cloud GraphQL API, например: `https://your-instance.saleor.cloud/graphql/`.
   - Убедитесь, что он заканчивается на `/graphql/`.

4. **SALEOR_APP_TOKEN**
   - Получите токен в Saleor Dashboard:
     - Перейдите в **Settings > API keys**.
     - Создайте ключ с разрешениями `MANAGE_CHANNELS` и `MANAGE_PRODUCTS`.
     - Вставьте токен в `SALEOR_APP_TOKEN`, например: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`.

5. **REDIS_URL**
   - Если используете локальный Redis: `redis://localhost:6379/0`.
   - Если используете Docker (как в `docker-compose.yml`): `redis://redis:6379/0`.

6. **CORS_ORIGINS**
   - Включите URL Saleor Cloud и локальный фронтенд: `["https://your-instance.saleor.cloud", "http://localhost:3000"]`.
   - Это позволяет вашему API принимать запросы от Saleor Dashboard и локального фронтенда.

## Создание `.env` файла

1. Создайте файл `.env` в корне проекта (`saleor-price-manager/`).
2. Скопируйте и заполните приведённый пример, заменив `SALEOR_API_URL` и `SALEOR_APP_TOKEN` на ваши значения.
3. Добавьте `.env` в `.gitignore`, чтобы не публиковать токены.

## Особенности локального тестирования без ngrok

1. **Ограничения вебхуков**:
   - Saleor Cloud не сможет отправлять вебхуки на `http://localhost:8000`, так как это локальный адрес.
   - Для тестирования вебхуков локально:
     - Используйте Postman или `curl` для отправки тестовых вебхук-запросов на `http://localhost:8000/webhooks/product-updated` или `http://localhost:8000/webhooks/channel-created`.
     - Пример тестового запроса:
       ```bash
       curl -X POST http://localhost:8000/webhooks/product-updated \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer your_saleor_app_token" \
       -d '{"event_type": "PRODUCT_UPDATED", "product_id": "UHJvZHVjdDox"}'
       ```

2. **Тестирование API**:
   - Используйте Swagger UI FastAPI по адресу `http://localhost:8000/docs` для проверки эндпоинтов, таких как `/api/channels` или `/api/prices/calculate`.
   - Убедитесь, что передаёте `SALEOR_APP_TOKEN` в заголовке `Authorization`.

3. **Тестирование фронтенда**:
   - Запустите фронтенд (`cd frontend && npm start`) и откройте `http://localhost:3000`.
   - Убедитесь, что в `frontend/package.json` или `.env` фронтенда установлен `REACT_APP_API_URL=http://localhost:8000`.

4. **Регистрация приложения**:
   - Без публичного URL (`APP_URL`) вы не сможете зарегистрировать приложение в Saleor Cloud через манифест, так как Saleor требует HTTPS для вебхуков.
   - Для тестирования API без регистрации используйте токен напрямую в запросах.
   - Если регистрация нужна, временно разверните приложение на облачной платформе (например, Heroku) или используйте SSH-туннель для создания публичного URL.

## Запуск приложения

1. **Запустите Redis**:
   - Если без Docker: `redis-server`.
   - Если с Docker: `docker-compose up redis`.

2. **Запустите FastAPI**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Запустите фронтенд**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Проверка**:
   - Откройте `http://localhost:8000/health` для проверки API.
   - Откройте `http://localhost:3000` для проверки фронтенда.
   - В Saleor Dashboard проверьте, что токен работает, выполнив тестовый GraphQL-запрос через Postman:
     ```graphql
     query {
       channels {
         id
         name
         slug
       }
     }
     ```
     С заголовком: `Authorization: Bearer your_saleor_app_token`.

## Альтернативы ngrok для публичного доступа

Если вы хотите протестировать вебхуки без ngrok, рассмотрите:

1. **Локальный туннель через SSH**:
   - Используйте сервер с публичным IP и настройте обратный туннель:
     ```bash
     ssh -R 80:localhost:8000 user@your-public-server.com
     ```
   - Это создаст публичный URL на сервере, который перенаправляет запросы на ваш локальный порт 8000.

2. **Cloudflare Tunnel**:
   - Установите `cloudflared` и настройте туннель для `localhost:8000` и `localhost:3000`.
   - Это предоставит HTTPS-URL без ngrok.

3. **Временное развертывание**:
   - Разверните приложение на бесплатной платформе (например, Render, Fly.io) для тестирования с публичным URL.

## Примечания

- **Вебхуки**: Без публичного URL тестирование вебхуков ограничено ручными запросами. Для полной интеграции рекомендуется временное развертывание или использование туннеля.
- **Безопасность**: Не используйте `http://localhost` в продакшене; HTTPS обязателен для Saleor Cloud.
- **CORS**: Если вы добавляете другие локальные URL, обновите `CORS_ORIGINS`.

---

# Точки соприкосновения с Saleor Cloud API

Для работы с Saleor Cloud вам понадобятся следующие основные точки соприкосновения и реквизиты:

## Основные эндпоинты Saleor

1. **GraphQL API** - основной эндпоинт для всех операций
   ```
   https://your-instance.saleor.cloud/graphql/
   ```

2. **Webhook API** - для регистрации вашего приложения и получения уведомлений
   ```
   https://your-instance.saleor.cloud/webhooks/
   ```

3. **App Manifest** - для установки вашего приложения в Saleor
   ```
   https://your-instance.saleor.cloud/app-manifest/
   ```

## Необходимые реквизиты

Одной ссылки на API недостаточно. Вам потребуются:

1. **JWT-токен** - для аутентификации API-запросов
   - Получается при авторизации приложения
   - Или можно создать токен в Dashboard Saleor (Settings > API keys)

2. **App API key и secret** - для регистрации вашего приложения
   - Генерируются при установке приложения через манифест

3. **Permissions (разрешения)** - необходимые для работы с каналами и ценами:
   - `MANAGE_CHANNELS` - для управления каналами
   - `MANAGE_PRODUCTS` - для работы с ценами продуктов
   - `MANAGE_DISCOUNTS` - если работаете со скидками

## Регистрация приложения

Для полноценной интеграции вам нужно зарегистрировать ваше приложение в Saleor:

```python
# app/saleor/client.py
from app.core.config import settings
import httpx

async def register_app():
    """Регистрация приложения в Saleor"""
    manifest = {
        "name": "Price Manager",
        "version": "1.0.0",
        "permissions": ["MANAGE_CHANNELS", "MANAGE_PRODUCTS"],
        "webhooks": [
            {
                "name": "Product updated",
                "targetUrl": f"{settings.APP_URL}/webhooks/product-updated",
                "events": ["PRODUCT_UPDATED"]
            },
            {
                "name": "Channel created",
                "targetUrl": f"{settings.APP_URL}/webhooks/channel-created",
                "events": ["CHANNEL_CREATED"]
            }
        ],
        "extensions": [
            {
                "label": "Price Manager",
                "mount": "NAVIGATION",
                "target": "CHANNELS",
                "permissions": ["MANAGE_CHANNELS"],
                "url": f"{settings.APP_FRONTEND_URL}"
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.SALEOR_API_URL}/app-manifest/",
            json=manifest
        )
        
        return response.json()
```

## Проверка наличия всего необходимого

Чтобы убедиться, что у вас есть всё для интеграции с Saleor Cloud:

1. URL GraphQL API (например, `https://your-instance.saleor.cloud/graphql/`)
2. Токен доступа с необходимыми разрешениями
3. Публично доступный URL для вашего приложения (для получения вебхуков)
4. URL для фронтенд-части приложения (для интеграции с Dashboard)

Если у вас есть только ссылка на API, вам нужно:
1. Получить токен доступа через Dashboard Saleor
2. Развернуть ваше приложение на публичном хостинге для получения вебхуков
3. Создать и загрузить манифест приложения для полноценной интеграции

При разработке можно использовать различные сервисы для туннелирования локального сервера.

---

# Формат APP_URL и APP_FRONTEND_URL

Для интеграции вашего FastAPI приложения с Saleor Cloud переменные `APP_URL` и `APP_FRONTEND_URL` должны быть настроены следующим образом:

## 1. APP_URL
Это публичный URL вашего FastAPI сервера, который обрабатывает API-запросы и вебхуки от Saleor. Он должен:

- Быть **доступным извне** (Saleor Cloud должен иметь возможность отправлять запросы к нему).
- Использовать **HTTPS** (Saleor Cloud требует защищённое соединение для вебхуков).
- Указывать на корень вашего API сервера.

**Пример:**
```
APP_URL=https://your-price-manager.example.com
```
- Если вы разрабатываете локально, можно использовать временный туннель через сервисы вроде ngrok:
  ```
  APP_URL=https://abc123.ngrok.io
  ```
- Для вебхуков Saleor будет отправлять запросы на подпути, например:
  ```
  https://your-price-manager.example.com/webhooks/product-updated
  ```

## 2. APP_FRONTEND_URL
Это публичный URL фронтенд-приложения (React или другой UI), который интегрируется в Saleor Dashboard. Он должен:

- Быть **доступным извне** и также использовать **HTTPS**.
- Указывать на корневую страницу вашего фронтенд-приложения, которое отображает интерфейс для управления наценками.
- Использоваться в манифесте приложения для отображения в Saleor Dashboard (например, в меню навигации).

**Пример:**
```
APP_FRONTEND_URL=https://your-price-manager.example.com/frontend
```
- Если фронтенд размещён на отдельном домене или поддомене:
  ```
  APP_FRONTEND_URL=https://frontend.your-price-manager.example.com
  ```
- Для локальной разработки с ngrok:
  ```
  APP_FRONTEND_URL=https://xyz789.ngrok.io
  ```

## Настройка в конфигурации
Эти переменные обычно задаются в файле конфигурации вашего приложения (например, `app/core/config.py`):

```python
# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_URL: str
    APP_FRONTEND_URL: str
    SALEOR_API_URL: str
    CORS_ORIGINS: list = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

И в `.env` файле:
```
APP_URL=https://your-price-manager.example.com
APP_FRONTEND_URL=https://frontend.your-price-manager.example.com
SALEOR_API_URL=https://your-instance.saleor.cloud/graphql/
CORS_ORIGINS=["https://your-instance.saleor.cloud"]
```

## Проверка корректности
- **APP_URL** должен быть доступен для Saleor Cloud для отправки вебхуков (проверьте доступность через `curl` или браузер).
- **APP_FRONTEND_URL** должен указывать на работающий фронтенд, который Saleor Dashboard сможет загрузить в iframe.
- Оба URL должны быть HTTPS (локально можно использовать самоподписанные сертификаты для тестирования с ngrok).

Если вы используете облачный хостинг (например, AWS, Heroku, Vercel), убедитесь, что ваш сервер и фронтенд развернуты и доступны по указанным адресам.
