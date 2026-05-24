from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from database.session import get_db
from auth.jwt import get_current_user
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse
from crud import order as order_crud

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
        order: OrderCreate,
        db: AsyncSession = Depends(get_db)
):
    new_order = await order_crud.create_order(db, order)
    return new_order


@router.get("", response_model=OrderListResponse)
async def list_orders(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        status: Optional[str] = None
):
    skip = (page - 1) * limit
    orders, total = await order_crud.get_orders(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )
    return OrderListResponse(orders=orders, total=total)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    order = await order_crud.get_order_by_id(db, order_uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
        order_id: str,
        status_update: OrderUpdate,
        db: AsyncSession = Depends(get_db),
_=Depends(get_current_user)
):
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    if not status_update.status:
        raise HTTPException(status_code=400, detail="Status is required")

    updated = await order_crud.update_order_status(db, order_uuid, status_update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated