from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.schemas import PriceCalculationRequest, PriceCalculationResponse
from app.services.price_calculator import calculate_price_with_markup, batch_calculate_prices
from app.services.markup_service import markup_service
from app.core.security import verify_token

router = APIRouter()

@router.post(
    "/calculate", 
    response_model=PriceCalculationResponse,
    summary="Calculate Product Price",
    description="""Calculate the final price for a product in a specific channel,
    applying the channel's markup percentage to the base price.
    
    **Formula:** `final_price = base_price * (1 + markup_percent / 100)`
    
    **Parameters:**
    - product_id: Base64 encoded Saleor product ID
    - channel_id: Base64 encoded Saleor channel ID  
    - base_price: Original price before markup
    
    **Returns:**
    - Detailed price calculation including base price, markup, and final price
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {"description": "Price calculated successfully"},
        400: {"description": "Calculation error"},
        401: {"description": "Authentication required or token invalid"},
        422: {"description": "Request validation failed"}
    }
)
async def calculate_price(request: PriceCalculationRequest, token: str = Depends(verify_token)):
    """Calculate product price with channel markup"""
    try:
        markup_percent = await markup_service.get_channel_markup(request.channel_id)
        final_price = await calculate_price_with_markup(
            request.product_id,
            request.channel_id,
            request.base_price
        )
        
        return PriceCalculationResponse(
            product_id=request.product_id,
            channel_id=request.channel_id,
            base_price=str(request.base_price),
            markup_percent=str(markup_percent),
            final_price=str(final_price),
            currency="USD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Price calculation failed: {str(e)}"
        )

@router.post(
    "/batch-calculate",
    response_model=List[PriceCalculationResponse],
    summary="Batch Calculate Prices",
    description="""Calculate prices for multiple products across different channels in a single request.
    
    Useful for bulk price updates or when processing large product catalogs.
    
    **Parameters:**
    - Array of price calculation requests, each containing:
      - product_id: Base64 encoded Saleor product ID
      - channel_id: Base64 encoded Saleor channel ID
      - base_price: Original price before markup
    
    **Returns:**
    - Array of detailed price calculations
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {"description": "Batch calculation completed"},
        400: {"description": "Batch calculation error"},
        401: {"description": "Authentication required or token invalid"},
        422: {"description": "Request validation failed"}
    }
)
async def batch_calculate(items: List[PriceCalculationRequest], token: str = Depends(verify_token)):
    """Batch calculate prices for multiple products"""
    try:
        results = []
        for item in items:
            markup_percent = await markup_service.get_channel_markup(item.channel_id)
            final_price = await calculate_price_with_markup(
                item.product_id,
                item.channel_id,
                item.base_price
            )
            
            results.append(PriceCalculationResponse(
                product_id=item.product_id,
                channel_id=item.channel_id,
                base_price=str(item.base_price),
                markup_percent=str(markup_percent),
                final_price=str(final_price),
                currency="USD"
            ))
            
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch calculation failed: {str(e)}"
        )
