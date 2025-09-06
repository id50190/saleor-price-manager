from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import PriceCalculationRequest, PriceCalculationResponse
from app.services.price_calculator import calculate_price_with_markup, batch_calculate_prices
from app.core.security import verify_token

router = APIRouter()

@router.post("/calculate", response_model=PriceCalculationResponse)
async def calculate_price(request: PriceCalculationRequest, token: str = Depends(verify_token)):
    """Рассчитывает цену продукта с учетом наценки канала"""
    try:
        final_price = await calculate_price_with_markup(
            request.product_id,
            request.channel_id,
            request.base_price
        )
        return PriceCalculationResponse(
            product_id=request.product_id,
            channel_id=request.channel_id,
            base_price=request.base_price,
            markup_percent=await markup_service.get_channel_markup(request.channel_id),
            final_price=final_price,
            currency="USD"  # Предполагаем валюту, можно настроить через Saleor API
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-calculate")
async def batch_calculate(items: list[PriceCalculationRequest], token: str = Depends(verify_token)):
    """Массовый расчет цен для списка продуктов"""
    try:
        batch_items = [
            {"product_id": item.product_id, "channel_id": item.channel_id, "base_price": item.base_price}
            for item in items
        ]
        results = await batch_calculate_prices(batch_items)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
