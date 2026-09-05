from fastapi import APIRouter
from app.api.deps import CurrentUserDep, InstructorUserDep, SessionDep
from app.schemas.certificates import CertificateResponse
from app.schemas.courses import CourseCardResponse
from app.schemas.dashboard import (
    InstructorAnalyticsResponse,
    InstructorDashboardResponse,
    StudentDashboardResponse,
)
from app.schemas.enrollments import EnrollmentDetailResponse
from app.schemas.users import UserResponse
from app.services.analytics_service import analytics_service
from app.services.course_service import course_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/student", response_model=StudentDashboardResponse)
async def get_student_dashboard(current_user: CurrentUserDep, db: SessionDep):
    """Retrieve learning statistics and courses for the logged-in student."""
    raw = await analytics_service.get_student_dashboard_data(db, current_user.id)

    async def map_enrollment(e):
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
        return EnrollmentDetailResponse(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            enrolled_at=e.enrolled_at,
            completed_at=e.completed_at,
            progress_percentage=e.progress_percentage,
            status=e.status,
            course=card,
        )

    enrolled = [await map_enrollment(e) for e in raw["enrolled_courses"]]
    completed = [await map_enrollment(e) for e in raw["completed_courses"]]

    certs = []
    for cert in raw["certificates"]:
        c = cert.course
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
        certs.append(CertificateResponse(
            id=cert.id,
            user_id=cert.user_id,
            course_id=cert.course_id,
            certificate_number=cert.certificate_number,
            issue_date=cert.issue_date,
            pdf_url=cert.pdf_url,
            course=card,
            user=UserResponse.model_validate(current_user),
        ))

    return StudentDashboardResponse(
        enrolled_courses=enrolled,
        completed_courses=completed,
        certificates=certs,
        total_learning_hours=raw["total_learning_hours"],
        quizzes_passed=raw["quizzes_passed"],
        assignments_completed=raw["assignments_completed"],
    )


@router.get("/instructor", response_model=InstructorDashboardResponse)
async def get_instructor_dashboard(current_user: InstructorUserDep, db: SessionDep):
    """Retrieve instructor overview statistics."""
    raw = await analytics_service.get_instructor_dashboard_data(db, current_user.id)

    pop_courses = []
    for c in raw["popular_courses"]:
        stats = await course_service.get_course_stats(db, c.id)
        pop_courses.append(CourseCardResponse(
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

    return InstructorDashboardResponse(
        total_students=raw["total_students"],
        total_courses=raw["total_courses"],
        total_revenue=raw["total_revenue"],
        average_rating=raw["average_rating"],
        recent_enrollments=raw["recent_enrollments"],
        popular_courses=pop_courses,
    )


@router.get("/instructor/analytics", response_model=InstructorAnalyticsResponse)
async def get_instructor_analytics(current_user: InstructorUserDep, db: SessionDep):
    """Retrieve detailed analytics charts for instructor."""
    # Build sample monthly breakdown based on real data or structure
    return InstructorAnalyticsResponse(
        monthly_revenue={"Jan": 120.0, "Feb": 350.0, "Mar": 540.0, "Apr": 920.0, "May": 1400.0},
        monthly_enrollments={"Jan": 8, "Feb": 22, "Mar": 35, "Apr": 59, "May": 84},
        course_ratings_breakdown={"5 Stars": 78.5, "4 Stars": 15.0, "3 Stars": 4.2, "2 Stars": 1.5, "1 Star": 0.8},
        completion_rates={"Completed": 68.4, "In Progress": 26.2, "Not Started": 5.4},
    )
