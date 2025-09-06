from pydantic import BaseModel, Field, validator
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
    
    @validator('markup_percent')
    def validate_markup(cls, v):
        return Decimal(round(v, 2))
    
    class Config:
        schema_extra = {
            "example": {
                "channel_id": "Q2hhbm5lbDox",
                "markup_percent": 15.5
            }
        }

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
    
    class Config:
        schema_extra = {
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

class PriceCalculationRequest(BaseModel):
    """Request model for price calculation"""
    product_id: str = Field(
        ..., 
        description="Base64 encoded Saleor product ID",
        example="UHJvZHVjdDox"
    )
    channel_id: str = Field(
        ..., 
        description="Base64 encoded Saleor channel ID",
        example="Q2hhbm5lbDox"
    )
    base_price: Decimal = Field(
        ..., 
        description="Base price before markup",
        example=100.00
    )
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "UHJvZHVjdDox",
                "channel_id": "Q2hhbm5lbDox",
                "base_price": 100.00
            }
        }

class PriceCalculationResponse(BaseModel):
    """Response model for price calculation"""
    product_id: str = Field(..., description="Base64 encoded Saleor product ID")
    channel_id: str = Field(..., description="Base64 encoded Saleor channel ID")
    base_price: str = Field(..., description="Original base price")
    markup_percent: str = Field(..., description="Applied markup percentage")
    final_price: str = Field(..., description="Final price after markup")
    currency: str = Field(default="USD", description="Currency code")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": "UHJvZHVjdDox",
                "channel_id": "Q2hhbm5lbDox",
                "base_price": "100.00",
                "markup_percent": "15.00",
                "final_price": "115.00",
                "currency": "USD"
            }
        }

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
    
    class Config:
        schema_extra = {
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
