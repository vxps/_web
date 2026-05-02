from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
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


class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    address: str = Field(..., min_length=5)
    status: Optional[str] = Field(default="new", pattern="^(new|processing|completed|cancelled)$")


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(new|processing|completed|cancelled)$")


class OrderResponse(OrderBase):
    id: uuid.UUID
    total_amount: Decimal
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int