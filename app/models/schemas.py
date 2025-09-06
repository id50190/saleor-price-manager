from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import List, Optional, Dict, Any

class ChannelMarkup(BaseModel):
    channel_id: str
    markup_percent: Decimal = Field(..., ge=0, le=1000)
    
    @validator('markup_percent')
    def validate_markup(cls, v):
        return Decimal(round(v, 2))

class PriceCalculationRequest(BaseModel):
    product_id: str
    channel_id: str
    base_price: Decimal

class PriceCalculationResponse(BaseModel):
    product_id: str
    channel_id: str
    base_price: Decimal
    markup_percent: Decimal
    final_price: Decimal
    currency: str

class SaleorWebhookPayload(BaseModel):
    event_type: str
    product_id: Optional[str] = None
    channel_id: Optional[str] = None
    data: Dict[str, Any] = {}
