import httpx
from app.core.config import settings

async def get_channel(channel_id: str):
    """Получает данные канала из Saleor"""
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
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SALEOR_API_URL,
            json={"query": query},
            headers={"Authorization": f"Bearer {settings.SALEOR_APP_TOKEN}"}
        )
        data = response.json()
        return data.get("data", {}).get("channels", [])

async def update_channel_metadata(channel_id: str, metadata: list):
    """Обновляет метаданные канала"""
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
        return not data.get("data", {}).get("updateMetadata", {}).get("errors")
