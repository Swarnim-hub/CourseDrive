from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, InstructorUserDep, SessionDep
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.models.course import Course
from app.models.user import UserRole
from app.schemas.assignments import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentSubmissionCreate,
    AssignmentSubmissionGrade,
    AssignmentSubmissionResponse,
    AssignmentUpdate,
)
from app.schemas.users import UserResponse
from app.services.storage_service import storage_service

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: AssignmentCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Create a new assignment."""
    course = await db.scalar(select(Course).where(Course.id == data.course_id))
    if not course:
        raise NotFoundException("Course", data.course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to create assignment for this course")

    assignment = Assignment(
        course_id=data.course_id,
        lesson_id=data.lesson_id,
        title=data.title,
        instructions=data.instructions,
        max_score=data.max_score,
        due_date=data.due_date,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, current_user: CurrentUserDep, db: SessionDep):
    """Get assignment details."""
    assignment = await db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException("Assignment", assignment_id)
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Update assignment details."""
    assignment = await db.scalar(
        select(Assignment).where(Assignment.id == assignment_id).options(selectinload(Assignment.course))
    )
    if not assignment:
        raise NotFoundException("Assignment", assignment_id)
    if current_user.role != UserRole.ADMIN and assignment.course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this assignment")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(assignment, k, v)

    await db.flush()
    await db.refresh(assignment)
    return assignment


@router.post("/{assignment_id}/file")
async def upload_submission_file(
    assignment_id: int,
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
):
    """Upload assignment submission attachment."""
    url = await storage_service.save_file(file, folder="assignments", resource_type="auto")
    return {"file_url": url}


@router.post("/{assignment_id}/submit", response_model=AssignmentSubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    data: AssignmentSubmissionCreate,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Submit or resubmit an assignment."""
    assignment = await db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException("Assignment", assignment_id)

    query = select(AssignmentSubmission).where(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.user_id == current_user.id,
    )
    submission = await db.scalar(query)

    if not submission:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            user_id=current_user.id,
            submission_text=data.submission_text,
            file_url=data.file_url,
            status=SubmissionStatus.SUBMITTED,
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(submission)
    else:
        submission.submission_text = data.submission_text
        submission.file_url = data.file_url
        submission.status = SubmissionStatus.SUBMITTED
        submission.submitted_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(submission)
    return AssignmentSubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        user_id=submission.user_id,
        user=UserResponse.model_validate(current_user),
        submission_text=submission.submission_text,
        file_url=submission.file_url,
        score=submission.score,
        feedback=submission.feedback,
        status=submission.status,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
    )


@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionResponse])
async def list_assignment_submissions(
    assignment_id: int,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """List all submissions for an assignment (Instructor only)."""
    assignment = await db.scalar(
        select(Assignment).where(Assignment.id == assignment_id).options(selectinload(Assignment.course))
    )
    if not assignment:
        raise NotFoundException("Assignment", assignment_id)
    if current_user.role != UserRole.ADMIN and assignment.course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to view submissions for this assignment")

    query = (
        select(AssignmentSubmission)
        .where(AssignmentSubmission.assignment_id == assignment_id)
        .options(selectinload(AssignmentSubmission.user))
        .order_by(AssignmentSubmission.submitted_at.desc())
    )
    result = await db.execute(query)
    submissions = list(result.scalars().all())

    return [
        AssignmentSubmissionResponse(
            id=s.id,
            assignment_id=s.assignment_id,
            user_id=s.user_id,
            user=UserResponse.model_validate(s.user) if s.user else None,
            submission_text=s.submission_text,
            file_url=s.file_url,
            score=s.score,
            feedback=s.feedback,
            status=s.status,
            submitted_at=s.submitted_at,
            graded_at=s.graded_at,
        )
        for s in submissions
    ]


@router.post("/submissions/{submission_id}/grade", response_model=AssignmentSubmissionResponse)
async def grade_assignment_submission(
    submission_id: int,
    data: AssignmentSubmissionGrade,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Grade a submission and return feedback."""
    query = (
        select(AssignmentSubmission)
        .where(AssignmentSubmission.id == submission_id)
        .options(
            selectinload(AssignmentSubmission.assignment).selectinload(Assignment.course),
            selectinload(AssignmentSubmission.user),
        )
    )
    submission = await db.scalar(query)
    if not submission:
        raise NotFoundException("Submission", submission_id)

    course = submission.assignment.course
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to grade this submission")

    if data.score > submission.assignment.max_score:
        raise BadRequestException(f"Score cannot exceed max score of {submission.assignment.max_score}")

    submission.score = data.score
    submission.feedback = data.feedback
    submission.status = data.status
    submission.graded_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(submission)

    return AssignmentSubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        user_id=submission.user_id,
        user=UserResponse.model_validate(submission.user) if submission.user else None,
        submission_text=submission.submission_text,
        file_url=submission.file_url,
        score=submission.score,
        feedback=submission.feedback,
        status=submission.status,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
    )
