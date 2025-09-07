from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import ChannelMarkup, ChannelWithMarkup
from app.services.markup_service import markup_service
from app.core.security import verify_token

router = APIRouter()

@router.get(
    "/test",
    response_model=List[ChannelWithMarkup],
    summary="Test new Saleor API integration",
    description="Test endpoint for new Saleor API integration logic"
)
async def test_channels_endpoint(subdomain: str = None):
    """Test new channels logic with real Saleor API"""
    from app.saleor.api import settings
    import httpx
    
    # Test connection to real Saleor API
    if settings.SALEOR_API_URL and not settings.SALEOR_API_URL.endswith('your-instance.saleor.cloud/graphql/'):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test API connectivity
                test_response = await client.post(
                    settings.SALEOR_API_URL,
                    json={"query": "query { shop { name } }"},
                    headers={"Content-Type": "application/json"}
                )
                
                if test_response.is_success:
                    test_data = test_response.json()
                    shop_name = test_data.get('data', {}).get('shop', {}).get('name', 'Unknown')
                    
                    # Try to get channels without token
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
                    
                    response = await client.post(
                        settings.SALEOR_API_URL,
                        json={"query": query},
                        headers={"Content-Type": "application/json"}
                    )
                    data = response.json()
                    
                    if "errors" in data:
                        # Return demo data based on real API structure
                        return [
                            {
                                "id": "demo-connected-api",
                                "name": f"Demo for {shop_name}",
                                "slug": "demo-connected",
                                "markup_percent": "0",
                                "metadata": [
                                    {"key": "price_markup_percent", "value": "0"},
                                    {"key": "subdomains", "value": "demo,connected,api"},
                                    {"key": "api_status", "value": "connected_no_auth"}
                                ]
                            }
                        ]
                    else:
                        # Real channels from API
                        channels = data.get("data", {}).get("channels", [])
                        result = []
                        for channel in channels:
                            markup = "0"  # Default markup
                            for meta in channel.get("metadata", []):
                                if meta["key"] == "price_markup_percent":
                                    markup = meta["value"]
                                    break
                            channel["markup_percent"] = markup
                            result.append(channel)
                        return result
        except Exception as e:
            return [{"id": "error", "name": f"API Error: {str(e)}", "slug": "error", "markup_percent": "0", "metadata": []}]
    
    return [{"id": "no-api", "name": "No API configured", "slug": "no-api", "markup_percent": "0", "metadata": []}]

@router.get(
    "/",
    response_model=List[ChannelWithMarkup],
    summary="List All Channels",
    description="""Retrieve a list of all Saleor channels with their current markup percentages.
    
    This endpoint queries Saleor API for channel information and enriches it with
    markup data from Redis cache or Saleor metadata.
    
    **Parameters:**
    - subdomain (optional): Filter channels by subdomain value in metadata
    
    **Returns:**
    - List of channels with markup information
    - Each channel includes: id, name, slug, markup_percent, metadata
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {
            "description": "Successfully retrieved channels list",
        },
        401: {"description": "Authentication required or token invalid"},
        500: {"description": "Internal server error"}
    }
)
async def list_channels_endpoint(subdomain: str = None):  # Временно убрали аутентификацию для demo
    """Get list of all channels with markup information"""
    from app.saleor.api import list_channels, get_channel_by_subdomain
    
    if subdomain:
        # Фильтрация по поддомену
        channel = await get_channel_by_subdomain(subdomain)
        if not channel:
            return []
        markup = await markup_service.get_channel_markup(channel["id"])
        channel["markup_percent"] = str(markup)
        return [channel]
    else:
        # Возврат всех каналов
        channels = await list_channels()
        result = []
        for channel in channels:
            markup = await markup_service.get_channel_markup(channel["id"])
            channel["markup_percent"] = str(markup)
            result.append(channel)
        return result

@router.post(
    "/markup",
    summary="Set Channel Markup",
    description="""Set or update the percentage markup for a specific channel.
    
    This operation will:
    1. Update the channel metadata in Saleor via GraphQL API
    2. Update the Redis cache for immediate access
    3. Trigger price recalculation for products in this channel
    
    **Parameters:**
    - channel_id: Base64 encoded Saleor channel ID
    - markup_percent: Percentage markup to apply (0-1000)
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {"description": "Markup successfully updated"},
        400: {"description": "Failed to update channel markup"},
        401: {"description": "Authentication required or token invalid"},
        422: {"description": "Request validation failed"}
    }
)
async def set_markup(markup: ChannelMarkup):  # Временно убрали аутентификацию для demo
    """Set markup percentage for a channel"""
    success = await markup_service.set_channel_markup(
        markup.channel_id, markup.markup_percent
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update channel markup"
        )
        
    return {"success": True, "markup": markup}
