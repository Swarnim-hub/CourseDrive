from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Query, status
from sqlalchemy import select
import redis.asyncio as redis

from app.api.deps import AdminUserDep, SessionDep
from app.config import settings
from app.core.exceptions import NotFoundException
from app.models.user import User, UserRole
from app.schemas.admin import AdminStatsResponse, AdminUserUpdate, SystemHealthResponse
from app.schemas.users import UserResponse
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(admin_user: AdminUserDep, db: SessionDep):
    """Retrieve platform-wide administration metrics."""
    return await analytics_service.get_admin_stats(db)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    admin_user: AdminUserDep,
    db: SessionDep,
    role: Optional[UserRole] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List users with filtering and pagination (Admin only)."""
    query = select(User).order_by(User.created_at.desc())
    if role:
        query = query.where(User.role == role)
    if search:
        pattern = f"%{search}%"
        query = query.where((User.email.ilike(pattern)) | (User.full_name.ilike(pattern)))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: AdminUserUpdate,
    admin_user: AdminUserDep,
    db: SessionDep,
):
    """Update user attributes (Admin only)."""
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise NotFoundException("User", user_id)

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(user, k, v)

    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin_user: AdminUserDep,
    db: SessionDep,
):
    """Delete a user (Admin only)."""
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise NotFoundException("User", user_id)
    await db.delete(user)
    await db.flush()


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(admin_user: AdminUserDep, db: SessionDep):
    """Check database and Redis health."""
    db_status = "healthy"
    redis_status = "healthy"

    try:
        await db.execute(select(1))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await r.ping()
        await r.close()
    except Exception as e:
        redis_status = f"unhealthy / standalone: {str(e)}"

    return SystemHealthResponse(
        status="ok" if db_status == "healthy" else "degraded",
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc),
    )
