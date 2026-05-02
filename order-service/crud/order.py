from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.order import Order
from models.order_item import OrderItem
from schemas.order import OrderCreate, OrderUpdate
from typing import Optional, List
from decimal import Decimal
import uuid


async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
    total_amount = sum(
        item.quantity * item.price_at_purchase
        for item in order_data.items
    )

    db_order = Order(
        customer_name=order_data.customer_name,
        email=order_data.email,
        address=order_data.address,
        status=order_data.status or "new",
        total_amount=total_amount
    )
    db.add(db_order)
    await db.flush()

    for item in order_data.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price_at_purchase=item.price_at_purchase
        )
        db.add(db_item)

    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_orders(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
) -> tuple[List[Order], int]:
    query = select(Order)

    if status:
        query = query.where(Order.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    for order in orders:
        await db.refresh(order, attribute_names=['items'])

    return orders, total


async def get_order_by_id(db: AsyncSession, order_id: uuid.UUID) -> Optional[Order]:
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if order:
        await db.refresh(order, attribute_names=['items'])

    return order


async def update_order_status(
        db: AsyncSession,
        order_id: uuid.UUID,
        new_status: str
) -> Optional[Order]:
    order = await get_order_by_id(db, order_id)
    if not order:
        return None

    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return order