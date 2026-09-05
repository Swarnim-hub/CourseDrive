from typing import Any, Dict, List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assignment import AssignmentSubmission, SubmissionStatus
from app.models.certificate import Certificate
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.payment import Payment, PaymentStatus
from app.models.progress import LessonProgress
from app.models.quiz import QuizAttempt
from app.models.review import Review
from app.models.user import User, UserRole


class AnalyticsService:
    async def get_student_dashboard_data(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Fetch stats and course lists for student dashboard."""
        enrollments_q = (
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .options(
                selectinload(Enrollment.course).selectinload(Course.instructor),
                selectinload(Enrollment.course).selectinload(Course.category),
            )
            .order_by(Enrollment.enrolled_at.desc())
        )
        result = await db.execute(enrollments_q)
        all_enrollments = list(result.scalars().all())

        enrolled_courses = [e for e in all_enrollments if e.status == EnrollmentStatus.ACTIVE]
        completed_courses = [e for e in all_enrollments if e.status == EnrollmentStatus.COMPLETED]

        # Certificates
        certs_q = (
            select(Certificate)
            .where(Certificate.user_id == user_id)
            .options(
                selectinload(Certificate.course).selectinload(Course.instructor),
                selectinload(Certificate.course).selectinload(Course.category),
            )
            .order_by(Certificate.issue_date.desc())
        )
        certs_result = await db.execute(certs_q)
        certificates = list(certs_result.scalars().all())

        # Quizzes passed
        quizzes_passed_q = select(func.count(QuizAttempt.id)).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.passed == True,
        )
        quizzes_passed = (await db.scalar(quizzes_passed_q)) or 0

        # Assignments completed
        assignments_done_q = select(func.count(AssignmentSubmission.id)).where(
            AssignmentSubmission.user_id == user_id,
            AssignmentSubmission.status == SubmissionStatus.GRADED,
        )
        assignments_completed = (await db.scalar(assignments_done_q)) or 0

        # Estimated total learning hours from completed lesson progresses
        hours_q = (
            select(func.coalesce(func.sum(LessonProgress.last_position_seconds), 0))
            .where(LessonProgress.user_id == user_id)
        )
        total_seconds = (await db.scalar(hours_q)) or 0
        total_learning_hours = round(total_seconds / 3600.0, 1)

        return {
            "enrolled_courses": enrolled_courses,
            "completed_courses": completed_courses,
            "certificates": certificates,
            "total_learning_hours": total_learning_hours,
            "quizzes_passed": quizzes_passed,
            "assignments_completed": assignments_completed,
        }

    async def get_instructor_dashboard_data(self, db: AsyncSession, instructor_id: int) -> Dict[str, Any]:
        """Fetch aggregate metrics for instructor dashboard."""
        # Total courses
        courses_q = (
            select(Course)
            .where(Course.instructor_id == instructor_id)
            .options(
                selectinload(Course.instructor),
                selectinload(Course.category),
            )
        )
        result = await db.execute(courses_q)
        courses = list(result.scalars().all())
        course_ids = [c.id for c in courses]
        total_courses = len(courses)

        if not course_ids:
            return {
                "total_students": 0,
                "total_courses": 0,
                "total_revenue": 0.0,
                "average_rating": 0.0,
                "recent_enrollments": [],
                "popular_courses": [],
            }

        # Total distinct students
        students_q = select(func.count(func.distinct(Enrollment.user_id))).where(
            Enrollment.course_id.in_(course_ids)
        )
        total_students = (await db.scalar(students_q)) or 0

        # Total revenue
        revenue_q = select(func.coalesce(func.sum(Payment.amount), 0.0)).where(
            Payment.course_id.in_(course_ids),
            Payment.status == PaymentStatus.SUCCEEDED,
        )
        total_revenue = float((await db.scalar(revenue_q)) or 0.0)

        # Average rating across instructor courses
        rating_q = select(func.coalesce(func.avg(Review.rating), 0.0)).where(
            Review.course_id.in_(course_ids)
        )
        avg_rating = round(float((await db.scalar(rating_q)) or 0.0), 1)

        # Recent enrollments
        recent_enroll_q = (
            select(Enrollment)
            .where(Enrollment.course_id.in_(course_ids))
            .options(selectinload(Enrollment.user), selectinload(Enrollment.course))
            .order_by(Enrollment.enrolled_at.desc())
            .limit(10)
        )
        recent_enrollments_res = await db.execute(recent_enroll_q)
        recent_enrollments = [
            {
                "student_name": e.user.full_name if e.user else "Anonymous",
                "course_title": e.course.title if e.course else "Course",
                "enrolled_at": e.enrolled_at.isoformat(),
                "progress_percentage": e.progress_percentage,
            }
            for e in recent_enrollments_res.scalars().all()
        ]

        return {
            "total_students": total_students,
            "total_courses": total_courses,
            "total_revenue": round(total_revenue, 2),
            "average_rating": avg_rating,
            "recent_enrollments": recent_enrollments,
            "popular_courses": courses[:5],
        }

    async def get_admin_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Fetch system-wide statistics for admin."""
        total_users = (await db.scalar(select(func.count(User.id)))) or 0
        total_instructors = (await db.scalar(select(func.count(User.id)).where(User.role == UserRole.INSTRUCTOR))) or 0
        total_students = (await db.scalar(select(func.count(User.id)).where(User.role == UserRole.STUDENT))) or 0
        total_courses = (await db.scalar(select(func.count(Course.id)))) or 0
        published_courses = (await db.scalar(select(func.count(Course.id)).where(Course.is_published == True))) or 0
        total_enrollments = (await db.scalar(select(func.count(Enrollment.id)))) or 0
        total_revenue = float((await db.scalar(select(func.coalesce(func.sum(Payment.amount), 0.0)).where(Payment.status == PaymentStatus.SUCCEEDED))) or 0.0)
        total_certificates = (await db.scalar(select(func.count(Certificate.id)))) or 0

        return {
            "total_users": total_users,
            "total_instructors": total_instructors,
            "total_students": total_students,
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_enrollments": total_enrollments,
            "total_revenue": round(total_revenue, 2),
            "total_certificates": total_certificates,
        }


analytics_service = AnalyticsService()
