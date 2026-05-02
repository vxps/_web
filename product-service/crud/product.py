from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from datetime import datetime
from decimal import Decimal
import uuid
from typing import Optional, List


async def get_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        active_only: bool = True,
        category_id: Optional[uuid.UUID] = None,
        bulb_type: Optional[str] = None,
        socket_type: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        search: Optional[str] = None
) -> tuple[List[Product], int]:
    query = select(Product)

    if active_only:
        query = query.where(Product.is_active == True, Product.deleted_at == None)

    if category_id:
        query = query.where(Product.category_id == category_id)
    if bulb_type:
        query = query.where(Product.bulb_type == bulb_type)
    if socket_type:
        query = query.where(Product.socket_type == socket_type)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()

    return products, total


async def get_product_by_id(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_active == True,
            Product.deleted_at == None
        )
    )
    return result.scalar_one_or_none()


async def get_product_by_id_admin(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.deleted_at == None
        )
    )
    return result.scalar_one_or_none()


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_product(db: AsyncSession, product_id: uuid.UUID, update_data: ProductUpdate) -> Optional[Product]:
    product = await get_product_by_id_admin(db, product_id)
    if not product:
        return None

    if update_data.price is not None and update_data.price != product.price:
        from models.price_history import PriceHistory
        price_change = PriceHistory(
            product_id=product_id,
            old_price=product.price,
            new_price=update_data.price
        )
        db.add(price_change)

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: uuid.UUID) -> bool:
    product = await get_product_by_id_admin(db, product_id)
    if not product:
        return False

    product.deleted_at = datetime.utcnow()
    await db.commit()
    return True


async def check_sku_exists(db: AsyncSession, sku: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
    query = select(Product.id).where(Product.sku == sku, Product.deleted_at == None)
    if exclude_id:
        query = query.where(Product.id != exclude_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None