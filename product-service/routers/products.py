from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal
import uuid

from database.session import get_db
from auth.jwt import get_current_user
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from crud import product as product_crud

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        active: bool = True,
        category_id: Optional[uuid.UUID] = None,
        bulb_type: Optional[str] = None,
        socket_type: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        search: Optional[str] = None
):
    skip = (page - 1) * limit

    products, total = await product_crud.get_products(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active,
        category_id=category_id,
        bulb_type=bulb_type,
        socket_type=socket_type,
        min_price=min_price,
        max_price=max_price,
        search=search
    )

    pages = (total + limit - 1) // limit

    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
        product_id: uuid.UUID,
        db: AsyncSession = Depends(get_db)
):
    product = await product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user)
):
    if await product_crud.check_sku_exists(db, product.sku):
        raise HTTPException(status_code=400, detail="SKU already exists")

    new_product = await product_crud.create_product(db, product)
    return new_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: uuid.UUID,
        product_update: ProductUpdate,
        db: AsyncSession = Depends(get_db),
_=Depends(get_current_user)
):
    if product_update.sku:
        if await product_crud.check_sku_exists(db, product_update.sku, exclude_id=product_id):
            raise HTTPException(status_code=400, detail="SKU already exists")

    updated = await product_crud.update_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}", status_code=204)
async def delete_product(
        product_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
_=Depends(get_current_user)
):
    success = await product_crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None