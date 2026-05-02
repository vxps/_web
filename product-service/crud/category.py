from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category
from schemas.category import CategoryCreate
from typing import Optional, List
import uuid


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Category]:
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: uuid.UUID) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def update_category(
        db: AsyncSession,
        category_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
) -> Optional[Category]:
    category = await get_category_by_id(db, category_id)
    if not category:
        return None

    if name is not None:
        category.name = name
    if description is not None:
        category.description = description

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: uuid.UUID) -> bool:
    category = await get_category_by_id(db, category_id)
    if not category:
        return False

    await db.delete(category)
    await db.commit()
    return True