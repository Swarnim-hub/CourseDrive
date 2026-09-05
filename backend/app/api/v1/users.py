from typing import List
from fastapi import APIRouter, File, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundException
from app.models.certificate import Certificate
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import User, UserRole
from app.schemas.courses import CourseCardResponse
from app.schemas.users import UserProfileResponse, UserResponse, UserUpdate
from app.services.storage_service import storage_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: CurrentUserDep, db: SessionDep):
    """Get full profile details for the authenticated user."""
    enrolled_count = (await db.scalar(
        select(func.count(Enrollment.id)).where(Enrollment.user_id == current_user.id)
    )) or 0

    completed_count = (await db.scalar(
        select(func.count(Enrollment.id)).where(
            Enrollment.user_id == current_user.id,
            Enrollment.status == EnrollmentStatus.COMPLETED,
        )
    )) or 0

    certs_count = (await db.scalar(
        select(func.count(Certificate.id)).where(Certificate.user_id == current_user.id)
    )) or 0

    instructed_count = None
    if current_user.role in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        instructed_count = (await db.scalar(
            select(func.count(Course.id)).where(Course.instructor_id == current_user.id)
        )) or 0

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        headline=current_user.headline,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        enrolled_courses_count=enrolled_count,
        completed_courses_count=completed_count,
        certificates_count=certs_count,
        instructed_courses_count=instructed_count,
    )


@router.put("/me", response_model=UserResponse)
async def update_my_profile(data: UserUpdate, current_user: CurrentUserDep, db: SessionDep):
    """Update profile information for the current user."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    current_user: CurrentUserDep,
    db: SessionDep,
    file: UploadFile = File(...),
):
    """Upload or update profile avatar image."""
    avatar_url = await storage_service.save_file(file, folder="avatars", resource_type="image")
    current_user.avatar_url = avatar_url
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_public_user_profile(user_id: int, db: SessionDep):
    """Get public profile of any user."""
    user = await db.scalar(select(User).where(User.id == user_id, User.is_active == True))
    if not user:
        raise NotFoundException("User", user_id)

    instructed_count = (await db.scalar(
        select(func.count(Course.id)).where(Course.instructor_id == user.id, Course.is_published == True)
    )) or 0

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        avatar_url=user.avatar_url,
        bio=user.bio,
        headline=user.headline,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        enrolled_courses_count=0,
        completed_courses_count=0,
        certificates_count=0,
        instructed_courses_count=instructed_count,
    )


@router.get("/{user_id}/courses", response_model=List[CourseCardResponse])
async def get_instructor_courses(user_id: int, db: SessionDep):
    """Get published courses created by a specific instructor."""
    query = (
        select(Course)
        .where(Course.instructor_id == user_id, Course.is_published == True)
        .options(selectinload(Course.instructor), selectinload(Course.category))
        .order_by(Course.created_at.desc())
    )
    result = await db.execute(query)
    courses = list(result.scalars().all())
    
    # Enrich course cards
    enriched: List[CourseCardResponse] = []
    for c in courses:
        stats = await course_service_stats(db, c.id)
        enriched.append(CourseCardResponse(
            id=c.id,
            title=c.title,
            slug=c.slug,
            subtitle=c.subtitle,
            thumbnail_url=c.thumbnail_url,
            level=c.level,
            price=float(c.price),
            is_free=c.is_free,
            is_published=c.is_published,
            instructor=UserResponse.model_validate(c.instructor),
            category=c.category,
            rating=stats["rating"],
            reviews_count=stats["reviews_count"],
            enrolled_count=stats["enrolled_count"],
            total_duration_seconds=c.total_duration_seconds,
            created_at=c.created_at,
        ))
    return enriched


async def course_service_stats(db: AsyncSession, course_id: int):
    from app.services.course_service import course_service
    return await course_service.get_course_stats(db, course_id)
