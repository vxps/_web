from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., ge=0)
    stock_quantity: int = Field(default=0, ge=0)

    bulb_type: Optional[str] = None
    wattage: Optional[int] = Field(None, ge=0)
    voltage: Optional[str] = None
    socket_type: Optional[str] = None
    color_temperature: Optional[int] = Field(None, ge=1000, le=10000)

    image_url: Optional[str] = None
    images: Optional[List[str]] = []

    is_active: bool = True
    category_id: Optional[uuid.UUID] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    bulb_type: Optional[str] = None
    wattage: Optional[int] = Field(None, ge=0)
    voltage: Optional[str] = None
    socket_type: Optional[str] = None
    color_temperature: Optional[int] = Field(None, ge=1000, le=10000)
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None
    category_id: Optional[uuid.UUID] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    limit: int
    pages: int