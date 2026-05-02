from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Boolean,
    DateTime, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.session import Base
import uuid


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)

    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)

    bulb_type = Column(String(50), nullable=True)
    wattage = Column(Integer, nullable=True)
    voltage = Column(String(50), nullable=True)
    socket_type = Column(String(50), nullable=True)
    color_temperature = Column(Integer, nullable=True)

    image_url = Column(Text, nullable=True)
    images = Column(ARRAY(String), nullable=True, default=[])

    is_active = Column(Boolean, default=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    category = relationship("Category", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")


from models.category import Category

Category.products = relationship("Product", back_populates="category", lazy="select")