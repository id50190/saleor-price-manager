# Production Deployment Guide

📋 **Руководство по развертыванию Saleor Price Manager в продакшене**

## 🚨 Важно: Различия между развертыванием и запуском

- **📦 `./DEPLOY`** - настройка среды разработки/тестирования
- **🔥 `./BANG`** - запуск для разработки (с автоперезагрузкой)
- **🏢 Продакшн** - используйте конфигурации ниже

---

## 🐳 Docker Production

### 1. Подготовка

```bash
# Создайте production .env файл
cp .env .env.production

# Отредактируйте production настройки
vim .env.production
```

### 2. Production .env конфигурация

```env
# Production URLs (замените на ваши домены)
APP_URL=https://price-manager.yourdomain.com
APP_FRONTEND_URL=https://price-manager.yourdomain.com/frontend

# Saleor Cloud производственные настройки
SALEOR_API_URL=https://your-production.saleor.cloud/graphql/
SALEOR_APP_TOKEN=your_production_saleor_token

# Production Redis (используйте внешний Redis)
REDIS_URL=redis://your-redis-server:6379/0

# Production CORS
CORS_ORIGINS=["https://your-production.saleor.cloud"]

# Application runtime (production settings)
APPLICATION_HOST=0.0.0.0
APPLICATION_PORT=8000
DEBUG=false
RELOAD=false
```

### 3. Docker Compose для продакшна

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_URL=${APP_URL}
      - APP_FRONTEND_URL=${APP_FRONTEND_URL}
      - SALEOR_API_URL=${SALEOR_API_URL}
      - REDIS_URL=redis://redis:6379/0
      - SALEOR_APP_TOKEN=${SALEOR_APP_TOKEN}
      - DEBUG=false
      - RELOAD=false
    restart: unless-stopped
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7.0-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  redis_data:
```

### 4. Запуск production

```bash
# Запуск в продакшене
docker-compose -f docker-compose.prod.yml up -d

# Мониторинг логов
docker-compose -f docker-compose.prod.yml logs -f

# Остановка
docker-compose -f docker-compose.prod.yml down
```

---

## 🖥️ Server Deployment (Ubuntu)

### 1. Системные требования

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y redis-server nginx supervisor
sudo apt install -y build-essential curl

# Установка Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### 2. Создание пользователя приложения

```bash
# Создание системного пользователя
sudo useradd -m -s /bin/bash saleor-price-manager
sudo usermod -aG sudo saleor-price-manager

# Переключение на пользователя приложения
sudo su - saleor-price-manager
```

### 3. Развертывание приложения

```bash
# Клонирование репозитория
cd /opt
sudo mkdir saleor-price-manager
sudo chown saleor-price-manager:saleor-price-manager saleor-price-manager
cd saleor-price-manager
git clone <your-repo> .

# Настройка окружения
./DEPLOY

# Создание production конфигурации
cp .env .env.production
vim .env.production  # настройте production параметры
```

### 4. Supervisor конфигурация

```bash
# /etc/supervisor/conf.d/saleor-price-manager.conf
sudo tee /etc/supervisor/conf.d/saleor-price-manager.conf << 'EOF'
[program:saleor-price-manager]
command=/opt/saleor-price-manager/env/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/saleor-price-manager
user=saleor-price-manager
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/saleor-price-manager.log
environment=PATH="/opt/saleor-price-manager/env/bin:%(ENV_PATH)s"
EOF

# Перезагрузка supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start saleor-price-manager
```

### 5. Nginx конфигурация

```nginx
# /etc/nginx/sites-available/saleor-price-manager
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# Включение сайта
sudo ln -s /etc/nginx/sites-available/saleor-price-manager /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 📋 Мониторинг и логи

### Проверка статуса сервисов

```bash
# Supervisor
sudo supervisorctl status saleor-price-manager

# Nginx
sudo systemctl status nginx

# Redis
sudo systemctl status redis-server

# Логи приложения
sudo tail -f /var/log/saleor-price-manager.log

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check мониторинг

```bash
# Проверка здоровья API
curl -f https://your-domain.com/health

# Автоматический мониторинг (добавьте в cron)
*/5 * * * * curl -f https://your-domain.com/health || echo "API is down" | mail -s "Alert" admin@yourdomain.com
```

---

## 🔒 Безопасность

### 1. Firewall настройки

```bash
# UFW конфигурация
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 2. SSL сертификаты (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Настройки безопасности Redis

```bash
# /etc/redis/redis.conf
sudo vim /etc/redis/redis.conf

# Настройки:
bind 127.0.0.1
requirepass your_strong_redis_password

# Перезапуск Redis
sudo systemctl restart redis-server
```

---

## 🔄 Обновления

### Процесс обновления приложения

```bash
# 1. Переключение на пользователя приложения
sudo su - saleor-price-manager
cd /opt/saleor-price-manager

# 2. Резервное копирование
cp .env.production .env.backup

# 3. Получение обновлений
git pull origin main

# 4. Обновление зависимостей
source env/bin/activate
pip install -r requirements.txt

# 5. Пересборка Rust модуля (если необходимо)
./BUILD

# 6. Перезапуск сервиса
sudo supervisorctl restart saleor-price-manager

# 7. Проверка работоспособности
curl -f https://your-domain.com/health
```

---

## 📊 Производительность

### Настройки для высокой нагрузки

```bash
# Увеличение количества worker'ов в supervisor
# /etc/supervisor/conf.d/saleor-price-manager.conf
command=/opt/saleor-price-manager/env/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8

# Настройка Redis для производительности
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
tcp-keepalive 60
```

### Мониторинг ресурсов

```bash
# Установка htop для мониторинга
sudo apt install htop

# Мониторинг использования Redis
redis-cli info memory
redis-cli info stats
```

---

**📌 Помните**: всегда тестируйте изменения на staging окружении перед развертыванием в продакшене!
