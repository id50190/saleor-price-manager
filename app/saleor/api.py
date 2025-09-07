import httpx
from app.core.config import settings

async def get_channel(channel_id: str):
    """Получает данные канала из Saleor"""
    # Demo-режим для тестирования
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        demo_channels = {
            "Q2hhbm5lbDox": {
                "id": "Q2hhbm5lbDox", 
                "name": "Default Channel", 
                "slug": "default-channel", 
                "metadata": [
                    {"key": "price_markup_percent", "value": "0"},
                    {"key": "subdomain", "value": "default"}
                ]
            },
            "Q2hhbm5lbDoy": {
                "id": "Q2hhbm5lbDoy", 
                "name": "Moscow Store", 
                "slug": "moscow", 
                "metadata": [
                    {"key": "price_markup_percent", "value": "15"},
                    {"key": "subdomain", "value": "moscow"}
                ]
            },
            "Q2hhbm5lbDoz": {
                "id": "Q2hhbm5lbDoz", 
                "name": "SPb Store", 
                "slug": "spb", 
                "metadata": [
                    {"key": "price_markup_percent", "value": "10"},
                    {"key": "subdomain", "value": "spb"}
                ]
            }
        }
        return demo_channels.get(channel_id)
    
    query = """
    query GetChannel($id: ID!) {
        channel(id: $id) {
            id
            name
            slug
            metadata {
                key
                value
            }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query, "variables": {"id": channel_id}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        if "errors" in data:
            print(f"Saleor API Error for channel {channel_id}: {data['errors']}")
            return None
        return data.get("data", {}).get("channel")

async def list_channels():
    """Получает список всех каналов"""
    query = """
    query {
        channels {
            id
            name
            slug
            metadata {
                key
                value
            }
        }
    }
    """
    
    # Если токен не настроен, возвращаем demo-данные
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        return [
            {
                "id": "Q2hhbm5lbDox", 
                "name": "Default Channel", 
                "slug": "default-channel",
                "metadata": [
                    {"key": "price_markup_percent", "value": "0"},
                    {"key": "subdomains", "value": "default,main,www"}
                ]
            },
            {
                "id": "Q2hhbm5lbDoy", 
                "name": "Moscow Store", 
                "slug": "moscow",
                "metadata": [
                    {"key": "price_markup_percent", "value": "15"},
                    {"key": "subdomains", "value": "moscow,msk,ru-moscow"}
                ]
            },
            {
                "id": "Q2hhbm5lbDoz", 
                "name": "SPb Store", 
                "slug": "spb",
                "metadata": [
                    {"key": "price_markup_percent", "value": "10"},
                    {"key": "subdomains", "value": "spb,piter,leningrad"}
                ]
            }
        ]
    
    # Используем реальный Saleor API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.SALEOR_API_URL,
                json={"query": query},
                headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"} if settings.SALEOR_APP_TOKEN != "your_saleor_app_token_here" else {}
            )
            data = response.json()
            
            # Если есть ошибки, возвращаем demo-данные
            if "errors" in data:
                print(f"Saleor API Error: {data['errors']}")
                print("Falling back to demo mode")
                return await _get_demo_channels_with_markup()
                
            channels = data.get("data", {}).get("channels", [])
            
            # Добавляем markup_percent из metadata для каждого канала
            for channel in channels:
                markup_found = False
                for meta in channel.get("metadata", []):
                    if meta["key"] == "price_markup_percent":
                        markup_found = True
                        break
                if not markup_found:
                    # Добавляем default markup если его нет
                    channel.setdefault("metadata", []).append(
                        {"key": "price_markup_percent", "value": "0"}
                    )
                    
            return channels
            
    except Exception as e:
        print(f"Error connecting to Saleor API: {e}")
        print("Falling back to demo mode")
        return await _get_demo_channels_with_markup()

async def _get_demo_channels_with_markup():
    """Возвращает demo каналы с настройками markup"""
    return [
        {
            "id": "demo-default", 
            "name": "Demo Default Channel", 
            "slug": "demo-default",
            "metadata": [
                {"key": "price_markup_percent", "value": "0"},
                {"key": "subdomains", "value": "demo,test,local"}
            ]
        },
        {
            "id": "demo-premium", 
            "name": "Demo Premium Channel", 
            "slug": "demo-premium",
            "metadata": [
                {"key": "price_markup_percent", "value": "20"},
                {"key": "subdomains", "value": "premium,vip,gold"}
            ]
        }
    ]

async def update_channel_metadata(channel_id: str, metadata: list):
    """Обновляет метаданные канала"""
    # Demo-режим: просто логируем операцию
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        print(f"DEMO: Would update channel {channel_id} metadata: {metadata}")
        return True  # Притворяемся, что обновление прошло успешно
    
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
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": mutation, "variables": {"id": channel_id, "input": metadata}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        if "errors" in data:
            print(f"Saleor API Error updating metadata for channel {channel_id}: {data['errors']}")
            return False
        return not data.get("data", {}).get("updateMetadata", {}).get("errors")

async def get_product_data(product_id: str):
    """Получает данные продукта из Saleor"""
    query = """
    query GetProduct($id: ID!) {
        product(id: $id) {
            id
            name
            slug
            variants {
                id
                name
                channelListings {
                    channel {
                        id
                        name
                        slug
                    }
                    price {
                        amount
                        currency
                    }
                }
            }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query, "variables": {"id": product_id}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        return data.get("data", {}).get("product")
async def get_channel_by_subdomain(subdomain: str):
    """Получает канал по поддомену (поддерживает множественные subdomains)"""
    # Используем ту же логику, что и endpoint /api/channels/
    from app.api.channels import get_real_channels_or_fallback
    channels = await get_real_channels_or_fallback()
    
    for channel in channels:
        for meta in channel.get("metadata", []):
            # Поддерживаем как одиночные subdomain, так и множественные subdomains
            if meta["key"] in ["subdomain", "subdomains"]:
                # Разделяем по запятым и проверяем каждый subdomain
                subdomains = [s.strip() for s in meta["value"].split(",")]
                if subdomain in subdomains:
                    return channel
                    
    # Если не нашли по subdomain, попробуем найти по slug
    for channel in channels:
        if channel["slug"] == subdomain:
            return channel
            
    return None

def get_channel_subdomains(channel):
    """Извлекает список subdomains для канала"""
    for meta in channel.get("metadata", []):
        if meta["key"] in ["subdomain", "subdomains"]:
            return [s.strip() for s in meta["value"].split(",")]
    return [channel["slug"]]  # fallback к slug канала

async def get_product(product_id: str):
    """Получает данные продукта из Saleor включая метаданные"""
    # Demo-режим для тестирования
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        demo_products = {
            "UHJvZHVjdDox": {
                "id": "UHJvZHVjdDox",
                "name": "Demo Product 1",
                "slug": "demo-product-1",
                "metadata": [
                    {"key": "discounts", "value": '[{"percent": 15, "cap": "150", "shedule": "* * * * *", "period": {"datetime_start": "01-01-2025T00:00:00Z", "datetime_end": "31-12-2025T23:59:59Z"}}]'}
                ]
            },
            "UHJvZHVjdDoy": {
                "id": "UHJvZHVjdDoy",
                "name": "Demo Product 2", 
                "slug": "demo-product-2",
                "metadata": [
                    {"key": "discounts", "value": '[{"percent": -10, "cap": "80", "shedule": "0 9-17 * * 1-5", "period": {"datetime_start": "01-01-2025T00:00:00Z", "datetime_end": "31-12-2025T23:59:59Z"}}]'}
                ]
            }
        }
        return demo_products.get(product_id)
    
    query = """
    query GetProduct($id: ID!) {
        product(id: $id) {
            id
            name
            slug
            metadata {
                key
                value
            }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query, "variables": {"id": product_id}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        if "errors" in data:
            print(f"Saleor API Error for product {product_id}: {data['errors']}")
            return None
        return data.get("data", {}).get("product")

async def get_products(channel_slug: str = None, first: int = 100):
    """Получает список продуктов с метаданными"""
    # Demo-режим
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        return [
            {
                "id": "UHJvZHVjdDox",
                "name": "Demo Product 1",
                "slug": "demo-product-1",
                "metadata": [
                    {"key": "discounts", "value": '[{"percent": 15, "cap": "150", "shedule": "* * * * *", "period": {"datetime_start": "01-01-2025T00:00:00Z", "datetime_end": "31-12-2025T23:59:59Z"}}]'}
                ]
            },
            {
                "id": "UHJvZHVjdDoy",
                "name": "Demo Product 2",
                "slug": "demo-product-2", 
                "metadata": [
                    {"key": "discounts", "value": '[{"percent": -10, "cap": "80", "shedule": "0 9-17 * * 1-5", "period": {"datetime_start": "01-01-2025T00:00:00Z", "datetime_end": "31-12-2025T23:59:59Z"}}]'}
                ]
            }
        ]
    
    query = """
    query GetProducts($channel: String, $first: Int!) {
        products(first: $first, channel: $channel) {
            edges {
                node {
                    id
                    name
                    slug
                    metadata {
                        key
                        value
                    }
                }
            }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query, "variables": {"channel": channel_slug, "first": first}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        if "errors" in data:
            print(f"Saleor API Error getting products: {data['errors']}")
            return []
        
        edges = data.get("data", {}).get("products", {}).get("edges", [])
        return [edge["node"] for edge in edges]

async def update_product_metadata(product_id: str, metadata: list):
    """Обновляет метаданные продукта"""
    # Demo-режим: просто логируем операцию
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        print(f"DEMO: Would update product {product_id} metadata: {metadata}")
        return True  # Притворяемся, что обновление прошло успешно
    
    mutation = """
    mutation UpdateProductMetadata($id: ID!, $input: [MetadataInput!]!) {
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
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": mutation, "variables": {"id": product_id, "input": metadata}},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        if "errors" in data:
            print(f"Saleor API Error updating product metadata for {product_id}: {data['errors']}")
            return False
        return not data.get("data", {}).get("updateMetadata", {}).get("errors")

async def set_product_discounts(product_id: str, discounts: list):
    """Устанавливает скидки для продукта в метаданных"""
    from app.services.discount_service import discount_service
    
    discounts_json = discount_service.format_discounts(discounts)
    metadata = [{"key": "discounts", "value": discounts_json}]
    return await update_product_metadata(product_id, metadata)
