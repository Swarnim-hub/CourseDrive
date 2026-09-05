from fastapi import APIRouter, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, InstructorUserDep, OptionalUserDep, SessionDep
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.lesson import Lesson
from app.models.progress import LessonProgress
from app.models.section import Section
from app.models.user import UserRole
from app.schemas.lessons import (
    LessonCreate,
    LessonDetailResponse,
    LessonProgressResponse,
    LessonResponse,
    LessonUpdate,
    ProgressUpdate,
)
from app.services.course_service import course_service
from app.services.enrollment_service import enrollment_service
from app.services.storage_service import storage_service

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    db: SessionDep,
    current_user: OptionalUserDep,
):
    """Get lesson details. Accessible if preview is enabled, or if user is enrolled, or if instructor/admin."""
    query = (
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.section).selectinload(Section.course),
            selectinload(Lesson.quiz),
            selectinload(Lesson.assignment),
        )
    )
    lesson = await db.scalar(query)
    if not lesson:
        raise NotFoundException("Lesson", lesson_id)

    course = lesson.section.course
    is_completed = False
    last_position = 0

    # Authorization checks
    has_access = lesson.is_preview
    if current_user:
        if current_user.role == UserRole.ADMIN or course.instructor_id == current_user.id:
            has_access = True
        else:
            enrollment = await db.scalar(
                select(Enrollment).where(
                    Enrollment.user_id == current_user.id,
                    Enrollment.course_id == course.id,
                    Enrollment.status.in_([EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]),
                )
            )
            if enrollment:
                has_access = True
                prog = await db.scalar(
                    select(LessonProgress).where(
                        LessonProgress.user_id == current_user.id,
                        LessonProgress.lesson_id == lesson.id,
                    )
                )
                if prog:
                    is_completed = prog.is_completed
                    last_position = prog.last_position_seconds

    if not has_access:
        raise ForbiddenException("Enrollment required to access this lesson")

    return LessonDetailResponse(
        id=lesson.id,
        section_id=lesson.section_id,
        title=lesson.title,
        lesson_type=lesson.lesson_type,
        content=lesson.content,
        video_url=lesson.video_url,
        duration_seconds=lesson.duration_seconds,
        is_preview=lesson.is_preview,
        order_index=lesson.order_index,
        created_at=lesson.created_at,
        is_completed=is_completed,
        last_position_seconds=last_position,
        quiz_id=lesson.quiz.id if lesson.quiz else None,
        assignment_id=lesson.assignment.id if lesson.assignment else None,
    )


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_lesson(
    data: LessonCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Create a new lesson under a section."""
    return await course_service.create_lesson(db, current_user, data)


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    data: LessonUpdate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Update a lesson."""
    return await course_service.update_lesson(db, lesson_id, current_user, data)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Delete a lesson."""
    await course_service.delete_lesson(db, lesson_id, current_user)


@router.post("/{lesson_id}/video")
async def upload_lesson_video(
    lesson_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
    file: UploadFile = File(...),
):
    """Upload a video file for a lesson."""
    lesson = await db.scalar(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(selectinload(Lesson.section).selectinload(Section.course))
    )
    if not lesson:
        raise NotFoundException("Lesson", lesson_id)
    if current_user.role != UserRole.ADMIN and lesson.section.course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this lesson")

    video_url = await storage_service.save_file(file, folder="videos", resource_type="video")
    lesson.video_url = video_url
    await db.flush()
    return {"video_url": video_url}


@router.post("/{lesson_id}/progress", response_model=LessonProgressResponse)
async def track_progress(
    lesson_id: int,
    data: ProgressUpdate,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Update learning progress for a lesson (playback position and completion status)."""
    return await enrollment_service.update_lesson_progress(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson_id,
        is_completed=data.is_completed,
        last_position_seconds=data.last_position_seconds,
    )
