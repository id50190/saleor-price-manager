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

async def init_saleor_client():
    """Инициализация клиента Saleor"""
    # Здесь можно добавить логику инициализации клиента
    # Например, проверку подключения к API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.SALEOR_API_URL,
                json={"query": "query { me { id email } }"},
                headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
            )
            if response.status_code == 200:
                print("Saleor client initialized successfully")
            else:
                print(f"Failed to initialize Saleor client: {response.status_code}")
    except Exception as e:
        print(f"Saleor client initialization error: {e}")