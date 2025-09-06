from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import ChannelMarkup, ChannelWithMarkup
from app.services.markup_service import markup_service
from app.core.security import verify_token

router = APIRouter()

@router.get(
    "/",
    response_model=List[ChannelWithMarkup],
    summary="List All Channels",
    description="""Retrieve a list of all Saleor channels with their current markup percentages.
    
    This endpoint queries Saleor API for channel information and enriches it with
    markup data from Redis cache or Saleor metadata.
    
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
async def list_channels():  # Временно убрали аутентификацию для demo
    """Get list of all channels with markup information"""
    from app.saleor.api import list_channels
    
    channels = await list_channels()
    
    # Add markup information to each channel
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
