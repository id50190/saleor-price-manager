from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, status
from app.models.schemas import SaleorWebhookPayload
from app.services.markup_service import markup_service
from app.services.price_calculator import batch_calculate_prices
from app.saleor.api import get_product_data

router = APIRouter()

@router.post(
    "/product-updated",
    summary="Handle Product Updated Webhook",
    description="""Webhook endpoint for Saleor PRODUCT_UPDATED events.
    
    When a product is updated in Saleor, this endpoint triggers
    background price recalculation for all channels.
    
    **Event Processing:**
    1. Validates the webhook payload
    2. Queues background task for price recalculation
    3. Updates prices across all channels for the product
    
    **Authentication:** No bearer token required (webhook signatures handled separately)
    
    **Background Processing:** Price calculations are performed asynchronously
    """,
    responses={
        200: {
            "description": "Webhook received and processed",
            "content": {
                "application/json": {
                    "example": {"status": "received"}
                }
            }
        },
        400: {
            "description": "Invalid webhook payload",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid webhook payload"}
                }
            }
        }
    }
)
async def handle_product_updated(payload: SaleorWebhookPayload, background_tasks: BackgroundTasks):
    """Handle Saleor product updated webhook"""
    if payload.event_type != "PRODUCT_UPDATED" or not payload.product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid webhook payload: missing product_id or wrong event_type"
        )
    
    background_tasks.add_task(recalculate_product_prices, payload.product_id)
    return {"status": "received"}

@router.post(
    "/channel-created",
    summary="Handle Channel Created Webhook",
    description="""Webhook endpoint for Saleor CHANNEL_CREATED events.
    
    When a new channel is created in Saleor, this endpoint
    invalidates related caches and prepares the channel for markup management.
    
    **Event Processing:**
    1. Validates the webhook payload
    2. Invalidates Redis cache for the new channel
    3. Prepares channel for markup configuration
    
    **Authentication:** No bearer token required (webhook signatures handled separately)
    """,
    responses={
        200: {
            "description": "Webhook received and processed",
            "content": {
                "application/json": {
                    "example": {"status": "received"}
                }
            }
        },
        400: {
            "description": "Invalid webhook payload",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid webhook payload"}
                }
            }
        }
    }
)
async def handle_channel_created(payload: SaleorWebhookPayload):
    """Handle Saleor channel created webhook"""
    if payload.event_type != "CHANNEL_CREATED" or not payload.channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid webhook payload: missing channel_id or wrong event_type"
        )
    
    # Invalidate cache for the new channel
    await markup_service.invalidate_cache(payload.channel_id)
    return {"status": "received"}

async def recalculate_product_prices(product_id: str):
    """Background task: recalculate prices for a product across all channels"""
    try:
        product_data = await get_product_data(product_id)
        if not product_data:
            print(f"Product {product_id} not found")
            return
        
        # Extract channel pricing information from product variants
        batch_items = []
        for variant in product_data.get("variants", []):
            for channel_listing in variant.get("channelListings", []):
                if channel_listing.get("price"):
                    batch_items.append({
                        "product_id": product_id,
                        "channel_id": channel_listing["channel"]["id"],
                        "base_price": float(channel_listing["price"]["amount"])
                    })
        
        if batch_items:
            await batch_calculate_prices(batch_items)
            print(f"Recalculated prices for product {product_id} across {len(batch_items)} channel(s)")
    except Exception as e:
        print(f"Error recalculating prices for product {product_id}: {str(e)}")
