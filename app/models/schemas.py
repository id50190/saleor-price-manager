from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal
from typing import List, Optional, Dict, Any

class ChannelMarkup(BaseModel):
    """Request model for setting channel markup percentage"""
    channel_id: str = Field(
        ..., 
        description="Base64 encoded Saleor channel ID",
        example="Q2hhbm5lbDox"
    )
    markup_percent: Decimal = Field(
        ..., 
        ge=0, 
        le=1000,
        description="Markup percentage to apply (0-1000)",
        example=15.5
    )
    
    @field_validator('markup_percent')
    @classmethod
    def validate_markup(cls, v):
        return Decimal(round(v, 2))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "channel_id": "Q2hhbm5lbDox",
                "markup_percent": 15.5
            }
        }
    )

class ChannelWithMarkup(BaseModel):
    """Channel information with markup data"""
    id: str = Field(..., description="Base64 encoded Saleor channel ID")
    name: str = Field(..., description="Human-readable channel name")
    slug: str = Field(..., description="URL-friendly channel identifier")
    markup_percent: str = Field(..., description="Current markup percentage")
    metadata: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Channel metadata from Saleor"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "Q2hhbm5lbDox",
                "name": "Moscow Store",
                "slug": "moscow",
                "markup_percent": "15.00",
                "metadata": [
                    {"key": "price_markup_percent", "value": "15.00"}
                ]
            }
        }
    )

class PriceCalculationRequest(BaseModel):
    """Request model for price calculation"""
    product_id: str = Field(
        ..., 
        min_length=1,
        description="Base64 encoded Saleor product ID",
        example="UHJvZHVjdDox"
    )
    channel_id: Optional[str] = Field(
        None, 
        min_length=1,
        description="Base64 encoded Saleor channel ID (optional if using subdomain)",
        example="Q2hhbm5lbDox"
    )
    base_price: Decimal = Field(
        ..., 
        gt=0,
        description="Base price before markup (must be positive)",
        example=100.00
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "UHJvZHVjdDox",
                "channel_id": "Q2hhbm5lbDox",
                "base_price": 100.00
            }
        }
    )
    
    @field_validator('channel_id')
    @classmethod
    def validate_channel_or_subdomain(cls, v):
        # Channel ID is optional if subdomain is used via query parameter
        return v

class PriceCalculationResponse(BaseModel):
    """Response model for price calculation"""
    product_id: str = Field(..., description="Base64 encoded Saleor product ID")
    channel_id: str = Field(..., description="Base64 encoded Saleor channel ID")
    base_price: str = Field(..., description="Original base price")
    markup_percent: str = Field(..., description="Applied markup percentage")
    discount_percent: Optional[str] = Field(None, description="Applied discount percentage (if any)")
    discount_applied: bool = Field(default=False, description="Whether a discount was applied")
    final_price: str = Field(..., description="Final price after markup and discount")
    currency: str = Field(default="USD", description="Currency code")
    active_discount: Optional[Dict[str, Any]] = Field(None, description="Details of applied discount")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_id": "UHJvZHVjdDox",
                "channel_id": "Q2hhbm5lbDox",
                "base_price": "100.00",
                "markup_percent": "15.00",
                "final_price": "115.00",
                "currency": "USD"
            }
        }
    )

class SaleorWebhookPayload(BaseModel):
    """Saleor webhook event payload"""
    event_type: str = Field(
        ..., 
        description="Type of Saleor event",
        example="PRODUCT_UPDATED"
    )
    product_id: Optional[str] = Field(
        None, 
        description="Product ID for product-related events",
        example="UHJvZHVjdDox"
    )
    channel_id: Optional[str] = Field(
        None, 
        description="Channel ID for channel-related events",
        example="Q2hhbm5lbDox"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event data from Saleor"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_type": "PRODUCT_UPDATED",
                "product_id": "UHJvZHVjdDox",
                "data": {
                    "product": {
                        "id": "UHJvZHVjdDox",
                        "name": "Sample Product"
                    }
                }
            }
        }
    )

class DiscountPeriod(BaseModel):
    """Discount period model"""
    datetime_start: str = Field(
        ..., 
        description="Start date in DD-MM-YYYYTHH:MM:SSZ format",
        example="01-01-2025T00:00:00Z"
    )
    datetime_end: str = Field(
        ..., 
        description="End date in DD-MM-YYYYTHH:MM:SSZ format",
        example="31-12-2025T23:59:59Z"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "datetime_start": "01-01-2025T00:00:00Z",
                "datetime_end": "31-12-2025T23:59:59Z"
            }
        }
    )

class ProductDiscount(BaseModel):
    """Product discount model"""
    percent: Decimal = Field(
        ..., 
        description="Discount percentage (+/-), positive for markup, negative for discount",
        example=10
    )
    cap: str = Field(
        ..., 
        description="Maximum/minimum price cap",
        example="2000"
    )
    shedule: str = Field(
        default="* * * * *",
        description="Cron schedule for when discount is active",
        example="5 4 * * *"
    )
    period: Optional[DiscountPeriod] = Field(
        None,
        description="Time period when discount is valid"
    )
    
    @field_validator('percent')
    @classmethod
    def validate_percent(cls, v):
        return Decimal(round(v, 2))
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "percent": 10,
                "cap": "2000",
                "shedule": "5 4 * * *",
                "period": {
                    "datetime_start": "01-01-2025T00:00:00Z",
                    "datetime_end": "31-12-2025T23:59:59Z"
                }
            }
        }
    )

class ProductDiscounts(BaseModel):
    """List of product discounts"""
    discounts: List[ProductDiscount] = Field(
        default_factory=list,
        description="List of product discounts"
    )

class ProductWithDiscounts(BaseModel):
    """Product with discount information"""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    slug: str = Field(..., description="Product slug")
    discounts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of all discounts for this product"
    )
    active_discount: Optional[Dict[str, Any]] = Field(
        None,
        description="Currently active discount (if any)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "UHJvZHVjdDox",
                "name": "Sample Product",
                "slug": "sample-product",
                "discounts": [
                    {
                        "percent": 10,
                        "cap": "2000",
                        "shedule": "* * * * *",
                        "period": {
                            "datetime_start": "01-01-2025T00:00:00Z",
                            "datetime_end": "31-12-2025T23:59:59Z"
                        }
                    }
                ],
                "active_discount": {
                    "percent": 10,
                    "cap": "2000",
                    "shedule": "* * * * *",
                    "period": {
                        "datetime_start": "01-01-2025T00:00:00Z",
                        "datetime_end": "31-12-2025T23:59:59Z"
                    }
                }
            }
        }
    )

class SetDiscountsRequest(BaseModel):
    """Request to set discounts for products"""
    discounts: List[ProductDiscount] = Field(
        ...,
        description="List of discounts to set"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "discounts": [
                    {
                        "percent": 15,
                        "cap": "150",
                        "shedule": "* * * * *",
                        "period": {
                            "datetime_start": "01-01-2025T00:00:00Z",
                            "datetime_end": "31-12-2025T23:59:59Z"
                        }
                    },
                    {
                        "percent": -10,
                        "cap": "80",
                        "shedule": "0 9-17 * * 1-5",
                        "period": {
                            "datetime_start": "01-06-2025T00:00:00Z",
                            "datetime_end": "30-06-2025T23:59:59Z"
                        }
                    }
                ]
            }
        }
    )
