from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.schemas import ProductDiscounts, ProductWithDiscounts, SetDiscountsRequest
from app.saleor.api import get_products, get_product, set_product_discounts
from app.services.discount_service import discount_service
from app.core.security import verify_token
from datetime import datetime
import pytz

router = APIRouter()

@router.get("/", response_model=List[ProductWithDiscounts])
async def list_products(
    channel_slug: Optional[str] = Query(None, description="Channel slug to filter products"),
    subdomain: Optional[str] = Query(None, description="Subdomain to identify channel"),
    first: int = Query(100, description="Number of products to fetch")
):
    """Get list of products with their discount information"""
    # Get products from Saleor
    products = await get_products(channel_slug, first)
    
    result = []
    for product in products:
        # Parse discounts
        discounts_json = next(
            (meta["value"] for meta in product.get("metadata", []) if meta["key"] == "discounts"),
            ""
        )
        discounts = discount_service.parse_discounts(discounts_json)
        
        # Find active discount
        active_discount = discount_service.get_active_discount(discounts)
        
        result.append(ProductWithDiscounts(
            id=product["id"],
            name=product["name"],
            slug=product["slug"],
            discounts=discounts,
            active_discount=active_discount
        ))
    
    return result

@router.get("/{product_id}", response_model=ProductWithDiscounts)
async def get_product_with_discounts(product_id: str):
    """Get product with its discount information"""
    product = await get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Parse discounts
    discounts_json = next(
        (meta["value"] for meta in product.get("metadata", []) if meta["key"] == "discounts"),
        ""
    )
    discounts = discount_service.parse_discounts(discounts_json)
    
    # Find active discount
    active_discount = discount_service.get_active_discount(discounts)
    
    return ProductWithDiscounts(
        id=product["id"],
        name=product["name"],
        slug=product["slug"],
        discounts=discounts,
        active_discount=active_discount
    )

@router.post("/{product_id}/discounts")
async def set_product_discounts_endpoint(
    product_id: str,
    request: SetDiscountsRequest
):
    """Set discounts for a product"""
    # Validate discounts
    errors = []
    for i, discount in enumerate(request.discounts):
        discount_errors = discount_service.validate_discount(discount.dict())
        if discount_errors:
            errors.extend([f"Discount {i}: {error}" for error in discount_errors])
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Convert to dict format
    discounts_list = [discount.dict() for discount in request.discounts]
    
    # Save to Saleor
    success = await set_product_discounts(product_id, discounts_list)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update product discounts"
        )
    
    return {"success": True, "discounts_count": len(discounts_list)}

@router.post("/batch-set-discounts")
async def batch_set_discounts(
    request: SetDiscountsRequest,
    channel_slug: Optional[str] = Query(None, description="Apply to products in specific channel only")
):
    """Set same discounts for all products (or products in specific channel)"""
    # Validate discounts
    errors = []
    for i, discount in enumerate(request.discounts):
        discount_errors = discount_service.validate_discount(discount.dict())
        if discount_errors:
            errors.extend([f"Discount {i}: {error}" for error in discount_errors])
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Get all products
    products = await get_products(channel_slug)
    
    # Convert to dict format
    discounts_list = [discount.dict() for discount in request.discounts]
    
    # Apply to all products
    success_count = 0
    for product in products:
        success = await set_product_discounts(product["id"], discounts_list)
        if success:
            success_count += 1
    
    return {
        "success": True, 
        "total_products": len(products),
        "updated_products": success_count,
        "discounts_count": len(discounts_list)
    }

@router.get("/{product_id}/active-discount")
async def get_active_discount(product_id: str):
    """Get currently active discount for a product"""
    product = await get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Parse discounts
    discounts_json = next(
        (meta["value"] for meta in product.get("metadata", []) if meta["key"] == "discounts"),
        ""
    )
    discounts = discount_service.parse_discounts(discounts_json)
    
    # Find active discount with current time info
    current_time = datetime.now(pytz.UTC)
    active_discount = discount_service.get_active_discount(discounts, current_time)
    
    return {
        "product_id": product_id,
        "current_time": current_time.isoformat(),
        "active_discount": active_discount,
        "total_discounts": len(discounts)
    }
