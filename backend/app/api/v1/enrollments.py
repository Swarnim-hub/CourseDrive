from typing import List, Optional
from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.schemas.courses import CourseCardResponse
from app.schemas.enrollments import EnrollmentCreate, EnrollmentDetailResponse, EnrollmentResponse
from app.schemas.users import UserResponse
from app.services.enrollment_service import enrollment_service
from app.services.course_service import course_service

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def enroll_course(data: EnrollmentCreate, current_user: CurrentUserDep, db: SessionDep):
    """Enroll student in a course (for free courses or direct enrollment)."""
    course = await db.scalar(select(Course).where(Course.id == data.course_id))
    if not course:
        raise NotFoundException("Course", data.course_id)

    if not course.is_free and course.price > 0:
        raise BadRequestException("This is a paid course. Please initiate checkout through /payments/checkout.")

    return await enrollment_service.enroll_student(db, current_user.id, data.course_id)


@router.get("/my", response_model=List[EnrollmentDetailResponse])
@router.get("/me", response_model=List[EnrollmentDetailResponse], include_in_schema=False)
async def get_my_enrollments(
    current_user: CurrentUserDep,
    db: SessionDep,
    status_filter: Optional[EnrollmentStatus] = Query(None, alias="status"),
):
    """List all courses enrolled by the current user."""
    enrollments = await enrollment_service.get_user_enrollments(db, current_user.id, status_filter)

    detailed: List[EnrollmentDetailResponse] = []
    for e in enrollments:
        c = e.course
        stats = await course_service.get_course_stats(db, c.id)
        card = CourseCardResponse(
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
        )
        detailed.append(EnrollmentDetailResponse(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            enrolled_at=e.enrolled_at,
            completed_at=e.completed_at,
            progress_percentage=e.progress_percentage,
            status=e.status,
            course=card,
        ))

    return detailed


@router.get("/course/{course_id}", response_model=Optional[EnrollmentResponse])
async def get_course_enrollment(course_id: int, current_user: CurrentUserDep, db: SessionDep):
    """Check if current user is enrolled in a specific course."""
    query = select(Enrollment).where(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id,
    )
    enrollment = await db.scalar(query)
    return enrollment
