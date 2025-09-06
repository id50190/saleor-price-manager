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
                    {"key": "subdomain", "value": "default"}
                ]
            },
            {
                "id": "Q2hhbm5lbDoy", 
                "name": "Moscow Store", 
                "slug": "moscow",
                "metadata": [
                    {"key": "price_markup_percent", "value": "15"},
                    {"key": "subdomain", "value": "moscow"}
                ]
            },
            {
                "id": "Q2hhbm5lbDoz", 
                "name": "SPb Store", 
                "slug": "spb",
                "metadata": [
                    {"key": "price_markup_percent", "value": "10"},
                    {"key": "subdomain", "value": "spb"}
                ]
            }
        ]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        
        # Если есть ошибки авторизации, возвращаем demo-данные
        if "errors" in data:
            print(f"Saleor API Error: {data['errors']}")
            return [
                {"id": "demo1", "name": "Demo Channel 1", "slug": "demo1", "metadata": []},
                {"id": "demo2", "name": "Demo Channel 2", "slug": "demo2", "metadata": []}
            ]
            
        return data.get("data", {}).get("channels", [])

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
    """Получает канал по поддомену"""
    # Demo-режим для тестирования
    if not settings.SALEOR_APP_TOKEN or settings.SALEOR_APP_TOKEN == "your_saleor_app_token_here":
        channels = await list_channels()
        for channel in channels:
            for meta in channel.get("metadata", []):
                if meta["key"] == "subdomain" and meta["value"] == subdomain:
                    return channel
        return None
    
    # Для реального Saleor API
    channels = await list_channels()
    for channel in channels:
        for meta in channel.get("metadata", []):
            if meta["key"] == "subdomain" and meta["value"] == subdomain:
                return channel
    return None

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
