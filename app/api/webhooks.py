from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.models.schemas import SaleorWebhookPayload
from app.services.markup_service import markup_service
from app.services.price_calculator import batch_calculate_prices
from app.saleor.api import get_product_data

router = APIRouter()

@router.post("/product-updated")
async def handle_product_updated(payload: SaleorWebhookPayload, background_tasks: BackgroundTasks):
    """Обработка события обновления продукта"""
    if payload.event_type != "PRODUCT_UPDATED" or not payload.product_id:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    
    background_tasks.add_task(recalculate_product_prices, payload.product_id)
    return {"status": "received"}

@router.post("/channel-created")
async def handle_channel_created(payload: SaleorWebhookPayload):
    """Обработка события создания канала"""
    if payload.event_type != "CHANNEL_CREATED" or not payload.channel_id:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")
    
    # Инвалидируем кэш для нового канала
    await markup_service.invalidate_cache(payload.channel_id)
    return {"status": "received"}

async def recalculate_product_prices(product_id: str):
    """Пересчитывает цены продукта для всех каналов"""
    product_data = await get_product_data(product_id)
    if not product_data:
        return
    
    channels = product_data.get("channels", [])
    batch_items = [
        {
            "product_id": product_id,
            "channel_id": channel["id"],
            "base_price": channel["price"]["amount"]
        }
        for channel in channels if channel.get("price")
    ]
    
    await batch_calculate_prices(batch_items)
