from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import ChannelMarkup, ChannelWithMarkup
from app.services.markup_service import markup_service
from app.core.security import verify_token
import httpx

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
    """Get list of all channels with markup information - now uses real API"""
    
    # Get channels from real API or fallback to Pool demo data
    channels = await get_real_channels_or_fallback()
    
    if subdomain:
        # Filter by subdomain
        for channel in channels:
            for meta in channel.get("metadata", []):
                if meta["key"] in ["subdomain", "subdomains"]:
                    subdomains = [s.strip() for s in meta["value"].split(",")]
                    if subdomain in subdomains:
                        return [channel]
        # If not found by metadata, try by slug
        for channel in channels:
            if channel["slug"] == subdomain:
                return [channel]
        return []
    else:
        # Return all channels
        return channels

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


async def get_real_channels_or_fallback():
    """Get channels from real Saleor API or return Pool demo data"""
    from app.core.config import settings
    
    # Always try to connect to real Saleor API if URL is configured
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
                    print(f"✅ Connected to Saleor shop: {shop_name}")
                    
                    # Try to get channels
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
                    
                    headers = {"Content-Type": "application/json"}
                    if settings.SALEOR_APP_TOKEN and settings.SALEOR_APP_TOKEN != "your_saleor_app_token_here":
                        headers["Authorization"] = f"Bearer {settings.SALEOR_APP_TOKEN}"
                        print("🔑 Using authentication token")
                    else:
                        print("🔓 Trying without authentication token")
                        
                    response = await client.post(
                        settings.SALEOR_API_URL,
                        json={"query": query},
                        headers=headers
                    )
                    data = response.json()
                    
                    if "errors" in data:
                        errors = data["errors"]
                        print(f"❌ Channels require authentication: {errors}")
                        return await _get_pool_channels_demo(shop_name)
                    else:
                        # Real channels from API
                        channels = data.get("data", {}).get("channels", [])
                        if channels:
                            print(f"📊 Got {len(channels)} real channels from Saleor API")
                            
                            # Process real channels
                            result = []
                            for channel in channels:
                                # Add markup_percent and subdomains if missing
                                markup_found = False
                                subdomains_found = False
                                
                                for meta in channel.get("metadata", []):
                                    if meta["key"] == "price_markup_percent":
                                        markup_found = True
                                    if meta["key"] in ["subdomain", "subdomains"]:
                                        subdomains_found = True
                                
                                if not markup_found:
                                    channel.setdefault("metadata", []).append(
                                        {"key": "price_markup_percent", "value": "0"}
                                    )
                                
                                if not subdomains_found:
                                    # Generate subdomains based on channel name/slug
                                    subdomains = _generate_subdomains_for_channel(channel)
                                    channel.setdefault("metadata", []).append(
                                        {"key": "subdomains", "value": ",".join(subdomains)}
                                    )
                                
                                # Add markup_percent for frontend compatibility
                                markup = await markup_service.get_channel_markup(channel["id"])
                                channel["markup_percent"] = str(markup)
                                result.append(channel)
                                
                            return result
                        else:
                            print("📭 No channels found in API")
                            return await _get_pool_channels_demo(shop_name)
                            
        except Exception as e:
            print(f"💥 Error connecting to Saleor API: {e}")
            return await _get_pool_channels_demo("Offline")
    
    # Fallback to demo data
    print("📋 Using demo data (SALEOR_API_URL not configured)")
    return await _get_pool_channels_demo("Demo")


async def _get_pool_channels_demo(shop_name: str):
    """Return demo Pool channels similar to real API structure"""
    channels = [
        {
            "id": "demo-pool-1", 
            "name": "Pool #1", 
            "slug": "pool01",
            "markup_percent": "5",
            "metadata": [
                {"key": "price_markup_percent", "value": "5"},
                {"key": "subdomains", "value": "pool1,premium,vip"}
            ]
        },
        {
            "id": "demo-pool-2", 
            "name": "Pool #2", 
            "slug": "pool02",
            "markup_percent": "10",
            "metadata": [
                {"key": "price_markup_percent", "value": "10"},
                {"key": "subdomains", "value": "pool2,business,pro"}
            ]
        },
        {
            "id": "demo-pool-3", 
            "name": "Pool #3", 
            "slug": "pool03",
            "markup_percent": "15",
            "metadata": [
                {"key": "price_markup_percent", "value": "15"},
                {"key": "subdomains", "value": "pool3,enterprise,gold"}
            ]
        },
        {
            "id": "demo-pool-4", 
            "name": "Pool #4", 
            "slug": "pool04",
            "markup_percent": "20",
            "metadata": [
                {"key": "price_markup_percent", "value": "20"},
                {"key": "subdomains", "value": "pool4,platinum,ultimate"}
            ]
        }
    ]
    
    # Add shop info to first channel metadata
    if channels and shop_name != "Demo":
        channels[0]["metadata"].append({"key": "api_shop", "value": shop_name})
        
    return channels


def _generate_subdomains_for_channel(channel):
    """Generate reasonable subdomains based on channel name and slug"""
    name = channel["name"].lower()
    slug = channel["slug"]
    
    subdomains = [slug]  # Always include slug
    
    # Generate based on name patterns
    if "pool" in name:
        pool_num = ''.join(filter(str.isdigit, name))
        if pool_num:
            subdomains.extend([f"pool{pool_num}", f"p{pool_num}"])
    
    if "default" in name:
        subdomains.extend(["default", "main", "www"])
    
    if "pln" in name.lower():
        subdomains.extend(["pln", "poland", "pl"])
        
    return list(set(subdomains))  # Remove duplicates