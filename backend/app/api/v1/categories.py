from typing import List, Optional
from fastapi import APIRouter, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import AdminUserDep, SessionDep
from app.core.exceptions import ConflictException, NotFoundException
from app.models.category import Category
from app.models.course import Course
from app.schemas.categories import CategoryCreate, CategoryResponse, CategoryTreeResponse, CategoryUpdate
from app.services.course_service import slugify

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
@router.get("/", response_model=List[CategoryResponse], include_in_schema=False)
async def get_categories(db: SessionDep):
    """Retrieve all categories with courses count."""
    query = select(Category).order_by(Category.name.asc())
    result = await db.execute(query)
    categories = list(result.scalars().all())

    response: List[CategoryResponse] = []
    for cat in categories:
        courses_count = (await db.scalar(
            select(func.count(Course.id)).where(Course.category_id == cat.id, Course.is_published == True)
        )) or 0
        response.append(CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            icon=cat.icon,
            parent_id=cat.parent_id,
            created_at=cat.created_at,
            courses_count=courses_count,
        ))
    return response


@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree(db: SessionDep):
    """Retrieve top-level categories with nested children."""
    query = select(Category).where(Category.parent_id == None).options(selectinload(Category.children)).order_by(Category.name.asc())
    result = await db.execute(query)
    parents = list(result.scalars().all())
    return parents


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: SessionDep):
    """Get single category details."""
    cat = await db.scalar(select(Category).where(Category.id == category_id))
    if not cat:
        raise NotFoundException("Category", category_id)
    courses_count = (await db.scalar(
        select(func.count(Course.id)).where(Course.category_id == cat.id, Course.is_published == True)
    )) or 0
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        description=cat.description,
        icon=cat.icon,
        parent_id=cat.parent_id,
        created_at=cat.created_at,
        courses_count=courses_count,
    )


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, admin_user: AdminUserDep, db: SessionDep):
    """Create a new category (Admin only)."""
    slug = data.slug or slugify(data.name)
    existing = await db.scalar(select(Category).where(Category.slug == slug))
    if existing:
        raise ConflictException(f"Category with slug '{slug}' already exists")

    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
        icon=data.icon,
        parent_id=data.parent_id,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, data: CategoryUpdate, admin_user: AdminUserDep, db: SessionDep):
    """Update an existing category (Admin only)."""
    category = await db.scalar(select(Category).where(Category.id == category_id))
    if not category:
        raise NotFoundException("Category", category_id)

    update_dict = data.model_dump(exclude_unset=True)
    if "name" in update_dict and not update_dict.get("slug"):
        update_dict["slug"] = slugify(update_dict["name"])

    for k, v in update_dict.items():
        setattr(category, k, v)

    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, admin_user: AdminUserDep, db: SessionDep):
    """Delete a category (Admin only)."""
    category = await db.scalar(select(Category).where(Category.id == category_id))
    if not category:
        raise NotFoundException("Category", category_id)
    await db.delete(category)
    await db.flush()
