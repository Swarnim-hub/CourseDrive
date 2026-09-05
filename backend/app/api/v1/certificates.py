from typing import List
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.certificate import Certificate
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.schemas.certificates import CertificateResponse, CertificateVerificationResponse
from app.schemas.courses import CourseCardResponse
from app.schemas.users import UserResponse
from app.services.certificate_service import certificate_service
from app.services.course_service import course_service

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/my", response_model=List[CertificateResponse])
async def get_my_certificates(current_user: CurrentUserDep, db: SessionDep):
    """Retrieve all certificates earned by the current user."""
    query = (
        select(Certificate)
        .where(Certificate.user_id == current_user.id)
        .options(
            selectinload(Certificate.course).selectinload(Course.instructor),
            selectinload(Certificate.course).selectinload(Course.category),
        )
        .order_by(Certificate.issue_date.desc())
    )
    result = await db.execute(query)
    certificates = list(result.scalars().all())

    response: List[CertificateResponse] = []
    for cert in certificates:
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
        response.append(CertificateResponse(
            id=cert.id,
            user_id=cert.user_id,
            course_id=cert.course_id,
            certificate_number=cert.certificate_number,
            issue_date=cert.issue_date,
            pdf_url=cert.pdf_url,
            course=card,
            user=UserResponse.model_validate(current_user),
        ))
    return response


@router.get("/course/{course_id}", response_model=CertificateResponse)
async def get_or_issue_course_certificate(course_id: int, current_user: CurrentUserDep, db: SessionDep):
    """Get or trigger generation of certificate for a completed course."""
    enrollment = await db.scalar(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id,
        )
    )
    if not enrollment:
        raise NotFoundException("Enrollment not found")

    if enrollment.progress_percentage < 100.0 and enrollment.status != EnrollmentStatus.COMPLETED:
        raise BadRequestException(f"Course is not yet complete. Current progress: {enrollment.progress_percentage}%")

    cert = await certificate_service.issue_certificate(db, current_user.id, course_id)
    course = await course_service.get_course_by_id(db, course_id)
    stats = await course_service.get_course_stats(db, course.id)

    card = CourseCardResponse(
        id=course.id,
        title=course.title,
        slug=course.slug,
        subtitle=course.subtitle,
        thumbnail_url=course.thumbnail_url,
        level=course.level,
        price=float(course.price),
        is_free=course.is_free,
        is_published=course.is_published,
        instructor=UserResponse.model_validate(course.instructor),
        category=course.category,
        rating=stats["rating"],
        reviews_count=stats["reviews_count"],
        enrolled_count=stats["enrolled_count"],
        total_duration_seconds=course.total_duration_seconds,
        created_at=course.created_at,
    )

    return CertificateResponse(
        id=cert.id,
        user_id=cert.user_id,
        course_id=cert.course_id,
        certificate_number=cert.certificate_number,
        issue_date=cert.issue_date,
        pdf_url=cert.pdf_url,
        course=card,
        user=UserResponse.model_validate(current_user),
    )


@router.get("/verify/{certificate_number}", response_model=CertificateVerificationResponse)
async def verify_certificate(certificate_number: str, db: SessionDep):
    """Public endpoint to verify authenticity of a certificate."""
    valid, cert = await certificate_service.verify_certificate(db, certificate_number)
    if not valid or not cert:
        return CertificateVerificationResponse(
            valid=False,
            certificate_number=certificate_number,
        )

    return CertificateVerificationResponse(
        valid=True,
        certificate_number=cert.certificate_number,
        student_name=cert.user.full_name,
        course_title=cert.course.title,
        instructor_name=cert.course.instructor.full_name if cert.course.instructor else "Instructor",
        issue_date=cert.issue_date,
        pdf_url=cert.pdf_url,
    )
