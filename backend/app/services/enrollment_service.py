from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.lesson import Lesson
from app.models.notification import Notification, NotificationType
from app.models.progress import LessonProgress
from app.models.section import Section
from app.services.certificate_service import certificate_service


class EnrollmentService:
    async def enroll_student(self, db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
        """Enroll a student into a course."""
        # Check course exists
        course = await db.scalar(select(Course).where(Course.id == course_id))
        if not course:
            raise NotFoundException("Course", course_id)

        # Check existing enrollment
        existing = await db.scalar(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        if existing:
            if existing.status == EnrollmentStatus.REFUNDED:
                existing.status = EnrollmentStatus.ACTIVE
                await db.flush()
                return existing
            return existing

        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.now(timezone.utc),
            progress_percentage=0.0,
            status=EnrollmentStatus.ACTIVE,
        )
        db.add(enrollment)

        # Create notification
        notif = Notification(
            user_id=user_id,
            title="Course Enrolled",
            message=f"You have successfully enrolled in '{course.title}'. Happy learning!",
            notification_type=NotificationType.ENROLLMENT,
            link=f"/learn/{course.slug}",
        )
        db.add(notif)

        await db.flush()
        await db.refresh(enrollment)
        return enrollment

    async def update_lesson_progress(
        self,
        db: AsyncSession,
        user_id: int,
        lesson_id: int,
        is_completed: Optional[bool] = None,
        last_position_seconds: Optional[int] = None,
    ) -> LessonProgress:
        """Update or create lesson progress and recalculate course completion."""
        # Find lesson and course
        lesson = await db.scalar(
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(selectinload(Lesson.section))
        )
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)

        course_id = lesson.section.course_id

        # Find or create lesson progress
        progress_q = select(LessonProgress).where(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id == lesson_id,
        )
        progress = await db.scalar(progress_q)

        if not progress:
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=bool(is_completed),
                last_position_seconds=last_position_seconds or 0,
                completed_at=datetime.now(timezone.utc) if is_completed else None,
            )
            db.add(progress)
        else:
            if is_completed is not None:
                progress.is_completed = is_completed
                if is_completed and not progress.completed_at:
                    progress.completed_at = datetime.now(timezone.utc)
                elif not is_completed:
                    progress.completed_at = None
            if last_position_seconds is not None:
                progress.last_position_seconds = last_position_seconds

        await db.flush()

        # Recalculate enrollment progress
        await self.recalculate_course_progress(db, user_id, course_id)

        await db.refresh(progress)
        return progress

    async def recalculate_course_progress(self, db: AsyncSession, user_id: int, course_id: int) -> float:
        """Calculate percentage of completed lessons in course."""
        # Total lessons in course
        total_lessons_q = (
            select(func.count(Lesson.id))
            .select_from(Lesson)
            .join(Section, Lesson.section_id == Section.id)
            .where(Section.course_id == course_id)
        )
        total_lessons = (await db.scalar(total_lessons_q)) or 0
        if total_lessons == 0:
            return 100.0

        # Completed lessons by user in this course
        completed_lessons_q = (
            select(func.count(LessonProgress.id))
            .select_from(LessonProgress)
            .join(Lesson, LessonProgress.lesson_id == Lesson.id)
            .join(Section, Lesson.section_id == Section.id)
            .where(
                Section.course_id == course_id,
                LessonProgress.user_id == user_id,
                LessonProgress.is_completed == True,
            )
        )
        completed_lessons = (await db.scalar(completed_lessons_q)) or 0
        percentage = round((completed_lessons / total_lessons) * 100.0, 1)

        # Update enrollment
        enrollment_q = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
        )
        enrollment = await db.scalar(enrollment_q)
        if enrollment:
            enrollment.progress_percentage = percentage
            if percentage >= 100.0 and enrollment.status != EnrollmentStatus.COMPLETED:
                enrollment.status = EnrollmentStatus.COMPLETED
                enrollment.completed_at = datetime.now(timezone.utc)
                # Automatically issue certificate
                try:
                    await certificate_service.issue_certificate(db, user_id, course_id)
                except Exception:
                    pass
            await db.flush()

        return percentage

    async def get_user_enrollments(
        self,
        db: AsyncSession,
        user_id: int,
        status: Optional[EnrollmentStatus] = None,
    ) -> List[Enrollment]:
        query = (
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .options(
                selectinload(Enrollment.course).selectinload(Course.instructor),
                selectinload(Enrollment.course).selectinload(Course.category),
            )
            .order_by(Enrollment.enrolled_at.desc())
        )
        if status:
            query = query.where(Enrollment.status == status)
        result = await db.execute(query)
        return list(result.scalars().all())


enrollment_service = EnrollmentService()
