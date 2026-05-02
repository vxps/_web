from pydantic import BaseModel, Field
from decimal import Decimal
import uuid


class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    product_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=1)
    price_at_purchase: Decimal = Field(..., ge=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: uuid.UUID

    class Config:
        from_attributes = True