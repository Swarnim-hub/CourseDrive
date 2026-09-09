import math
from typing import Optional
from fastapi import APIRouter, File, Query, UploadFile, status
from sqlalchemy import select
from app.api.deps import InstructorUserDep, OptionalUserDep, SessionDep
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.course import Course, CourseLevel
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import UserRole
from app.schemas.courses import (
    CourseCardResponse,
    CourseCreate,
    CourseDetailResponse,
    CourseListResponse,
    CourseUpdate,
)
from app.schemas.sections import SectionCreate, SectionResponse, SectionUpdate
from app.schemas.users import UserResponse
from app.services.course_service import course_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=CourseListResponse)
@router.get("/", response_model=CourseListResponse, include_in_schema=False)
async def list_courses(
    db: SessionDep,
    search: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Category filter"),
    level: Optional[CourseLevel] = Query(None, description="Level filter"),
    is_free: Optional[bool] = Query(None, description="Free or Paid"),
    instructor_id: Optional[int] = Query(None, description="Instructor ID filter"),
    sort_by: str = Query("newest", enum=["newest", "oldest", "price_low", "price_high"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """List published courses with filtering and pagination."""
    courses, total = await course_service.list_courses(
        db=db,
        search=search,
        category_id=category_id,
        level=level,
        is_free=is_free,
        is_published=True if not instructor_id else None,
        instructor_id=instructor_id,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )

    items = []
    for c in courses:
        stats = await course_service.get_course_stats(db, c.id)
        items.append(CourseCardResponse(
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

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return CourseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{id_or_slug}", response_model=CourseDetailResponse)
async def get_course_detail(
    id_or_slug: str,
    db: SessionDep,
    current_user: OptionalUserDep,
):
    """Retrieve full course details by ID or slug."""
    if id_or_slug.isdigit():
        course = await course_service.get_course_by_id(db, int(id_or_slug))
    else:
        course = await course_service.get_course_by_slug(db, id_or_slug)

    if not course:
        raise NotFoundException("Course", id_or_slug)

    # Check enrollment
    is_enrolled = False
    enrollment_status = None
    progress_pct = None

    if current_user:
        enroll_q = select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course.id,
        )
        enrollment = await db.scalar(enroll_q)
        if enrollment:
            is_enrolled = True
            enrollment_status = enrollment.status.value
            progress_pct = enrollment.progress_percentage

    # Fetch rating stats
    stats = await course_service.get_course_stats(db, course.id)

    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        slug=course.slug,
        subtitle=course.subtitle,
        description=course.description,
        requirements=course.requirements or [],
        what_you_will_learn=course.what_you_will_learn or [],
        level=course.level,
        language=course.language,
        price=float(course.price),
        is_free=course.is_free,
        is_published=course.is_published,
        promotional_video_url=course.promotional_video_url,
        thumbnail_url=course.thumbnail_url,
        total_duration_seconds=course.total_duration_seconds,
        created_at=course.created_at,
        updated_at=course.updated_at,
        instructor=UserResponse.model_validate(course.instructor),
        category=course.category,
        sections=[SectionResponse.model_validate(s) for s in sorted(course.sections, key=lambda x: x.order_index)],
        rating=stats["rating"],
        reviews_count=stats["reviews_count"],
        enrolled_count=stats["enrolled_count"],
        is_enrolled=is_enrolled,
        enrollment_status=enrollment_status,
        progress_percentage=progress_pct,
    )


@router.post("", response_model=CourseDetailResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CourseDetailResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_course(
    data: CourseCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Create a new course (Instructors & Admins only)."""
    course = await course_service.create_course(db, current_user.id, data)
    full_course = await course_service.get_course_by_id(db, course.id)
    return CourseDetailResponse(
        id=full_course.id,
        title=full_course.title,
        slug=full_course.slug,
        subtitle=full_course.subtitle,
        description=full_course.description,
        requirements=full_course.requirements or [],
        what_you_will_learn=full_course.what_you_will_learn or [],
        level=full_course.level,
        language=full_course.language,
        price=float(full_course.price),
        is_free=full_course.is_free,
        is_published=full_course.is_published,
        promotional_video_url=full_course.promotional_video_url,
        thumbnail_url=full_course.thumbnail_url,
        total_duration_seconds=full_course.total_duration_seconds,
        created_at=full_course.created_at,
        updated_at=full_course.updated_at,
        instructor=UserResponse.model_validate(full_course.instructor),
        category=full_course.category,
        sections=[],
        rating=0.0,
        reviews_count=0,
        enrolled_count=0,
        is_enrolled=False,
    )


@router.put("/{course_id}", response_model=CourseDetailResponse)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Update course information."""
    course = await course_service.update_course(db, course_id, current_user, data)
    full_course = await course_service.get_course_by_id(db, course.id)
    stats = await course_service.get_course_stats(db, full_course.id)

    return CourseDetailResponse(
        id=full_course.id,
        title=full_course.title,
        slug=full_course.slug,
        subtitle=full_course.subtitle,
        description=full_course.description,
        requirements=full_course.requirements or [],
        what_you_will_learn=full_course.what_you_will_learn or [],
        level=full_course.level,
        language=full_course.language,
        price=float(full_course.price),
        is_free=full_course.is_free,
        is_published=full_course.is_published,
        promotional_video_url=full_course.promotional_video_url,
        thumbnail_url=full_course.thumbnail_url,
        total_duration_seconds=full_course.total_duration_seconds,
        created_at=full_course.created_at,
        updated_at=full_course.updated_at,
        instructor=UserResponse.model_validate(full_course.instructor),
        category=full_course.category,
        sections=[SectionResponse.model_validate(s) for s in sorted(full_course.sections, key=lambda x: x.order_index)],
        rating=stats["rating"],
        reviews_count=stats["reviews_count"],
        enrolled_count=stats["enrolled_count"],
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, current_user: InstructorUserDep, db: SessionDep):
    """Delete a course."""
    course = await course_service.get_course_by_id(db, course_id)
    if not course:
        raise NotFoundException("Course", course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to delete this course")

    await db.delete(course)
    await db.flush()


@router.post("/{course_id}/thumbnail")
async def upload_course_thumbnail(
    course_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
    file: UploadFile = File(...),
):
    """Upload course thumbnail."""
    course = await course_service.get_course_by_id(db, course_id)
    if not course:
        raise NotFoundException("Course", course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this course")

    url = await storage_service.save_file(file, folder="thumbnails", resource_type="image")
    course.thumbnail_url = url
    await db.flush()
    return {"thumbnail_url": url}


@router.post("/{course_id}/publish")
async def toggle_course_publish(
    course_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Toggle publish status for a course."""
    course = await course_service.get_course_by_id(db, course_id)
    if not course:
        raise NotFoundException("Course", course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this course")

    course.is_published = not course.is_published
    await db.flush()
    return {"is_published": course.is_published}


# Section endpoints
@router.post("/{course_id}/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    course_id: int,
    data: SectionCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    data.course_id = course_id
    section = await course_service.create_section(db, current_user, data)
    return section


@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_section(
    section_id: int,
    data: SectionUpdate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    section = await course_service.update_section(db, section_id, current_user, data)
    return section


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    await course_service.delete_section(db, section_id, current_user)
