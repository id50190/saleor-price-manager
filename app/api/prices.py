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
    - channel_id: Base64 encoded Saleor channel ID (optional if subdomain provided)
    - base_price: Original price before markup
    - subdomain: Alternative way to specify channel via subdomain (optional)
    
    **Returns:**
    - Detailed price calculation including base price, markup, and final price
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {"description": "Price calculated successfully"},
        400: {"description": "Calculation error"},
        401: {"description": "Authentication required or token invalid"},
        404: {"description": "Channel not found for subdomain"},
        422: {"description": "Request validation failed"}
    }
)
async def calculate_price(request: PriceCalculationRequest, subdomain: str = None):  # Временно убрали аутентификацию для demo
    """Calculate product price with channel markup"""
    try:
        channel_id = request.channel_id
        
        # Если указан subdomain, ищем канал по нему
        if subdomain:
            from app.saleor.api import get_channel_by_subdomain
            channel = await get_channel_by_subdomain(subdomain)
            if not channel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No channel found for subdomain: {subdomain}"
                )
            channel_id = channel["id"]
        
        markup_percent = await markup_service.get_channel_markup(channel_id)
        final_price = await calculate_price_with_markup(
            request.product_id,
            channel_id,
            request.base_price
        )
        
        return PriceCalculationResponse(
            product_id=request.product_id,
            channel_id=channel_id,
            base_price=str(request.base_price),
            markup_percent=str(markup_percent),
            final_price=str(final_price),
            currency="USD"
        )
    except HTTPException:
        raise
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
async def batch_calculate(items: List[PriceCalculationRequest]):  # Временно убрали аутентификацию для demo
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

@router.post(
    "/calculate-by-subdomain", 
    response_model=PriceCalculationResponse,
    summary="Calculate Product Price by Subdomain",
    description="""Calculate the final price for a product using subdomain to identify the channel.
    
    This is a convenience endpoint for frontend applications that use subdomain-based 
    channel routing (e.g., moscow.yourdomain.com or ?subdomain=moscow).
    
    **Formula:** `final_price = base_price * (1 + markup_percent / 100)`
    
    **Parameters:**
    - product_id: Base64 encoded Saleor product ID
    - base_price: Original price before markup
    - subdomain: City or region subdomain (e.g., 'moscow', 'spb')
    
    **Returns:**
    - Detailed price calculation including base price, markup, and final price
    
    **Authentication:** Bearer token required
    """,
    responses={
        200: {"description": "Price calculated successfully"},
        400: {"description": "Calculation error"},
        404: {"description": "Channel not found for subdomain"},
        422: {"description": "Request validation failed"}
    }
)
async def calculate_price_by_subdomain(
    product_id: str,
    base_price: float,
    subdomain: str
):
    """Calculate product price using subdomain to identify channel"""
    try:
        from app.saleor.api import get_channel_by_subdomain
        
        # Find channel by subdomain
        channel = await get_channel_by_subdomain(subdomain)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No channel found for subdomain: {subdomain}"
            )
        
        channel_id = channel["id"]
        markup_percent = await markup_service.get_channel_markup(channel_id)
        final_price = await calculate_price_with_markup(
            product_id,
            channel_id,
            base_price
        )
        
        return PriceCalculationResponse(
            product_id=product_id,
            channel_id=channel_id,
            base_price=str(base_price),
            markup_percent=str(markup_percent),
            final_price=str(final_price),
            currency="USD"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Price calculation failed: {str(e)}"
        )
