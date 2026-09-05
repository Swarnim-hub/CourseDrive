from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, InstructorUserDep, SessionDep
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.course import Course
from app.models.quiz import QuestionType, Quiz, QuizAttempt, QuizQuestion
from app.models.user import UserRole
from app.schemas.quizzes import (
    QuizAttemptResponse,
    QuizAttemptSubmit,
    QuizCreate,
    QuizDetailResponse,
    QuizQuestionCreate,
    QuizQuestionResponse,
    QuizResponse,
    QuizUpdate,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("/", response_model=QuizDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    data: QuizCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Create a new quiz for a course/lesson."""
    course = await db.scalar(select(Course).where(Course.id == data.course_id))
    if not course:
        raise NotFoundException("Course", data.course_id)
    if current_user.role != UserRole.ADMIN and course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to add quiz to this course")

    quiz = Quiz(
        course_id=data.course_id,
        lesson_id=data.lesson_id,
        title=data.title,
        passing_score=data.passing_score,
        time_limit_minutes=data.time_limit_minutes,
    )
    db.add(quiz)
    await db.flush()

    if data.questions:
        for idx, q in enumerate(data.questions):
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                correct_answers=q.correct_answers,
                points=q.points,
                explanation=q.explanation,
                order_index=q.order_index if q.order_index else idx,
            )
            db.add(question)
        await db.flush()

    await db.refresh(quiz)
    # Reload with questions
    full_quiz = await db.scalar(
        select(Quiz).where(Quiz.id == quiz.id).options(selectinload(Quiz.questions))
    )
    return full_quiz


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(quiz_id: int, current_user: CurrentUserDep, db: SessionDep):
    """Get quiz details and questions for taking the test."""
    query = select(Quiz).where(Quiz.id == quiz_id).options(selectinload(Quiz.questions))
    quiz = await db.scalar(query)
    if not quiz:
        raise NotFoundException("Quiz", quiz_id)

    # Questions returned exclude correct_answers by schema validation
    return quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: int,
    data: QuizUpdate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Update quiz metadata."""
    quiz = await db.scalar(select(Quiz).where(Quiz.id == quiz_id).options(selectinload(Quiz.course)))
    if not quiz:
        raise NotFoundException("Quiz", quiz_id)
    if current_user.role != UserRole.ADMIN and quiz.course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this quiz")

    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(quiz, k, v)

    await db.flush()
    await db.refresh(quiz)
    return quiz


@router.post("/{quiz_id}/questions", response_model=QuizQuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_quiz_question(
    quiz_id: int,
    data: QuizQuestionCreate,
    current_user: InstructorUserDep,
    db: SessionDep,
):
    """Add a question to an existing quiz."""
    quiz = await db.scalar(select(Quiz).where(Quiz.id == quiz_id).options(selectinload(Quiz.course)))
    if not quiz:
        raise NotFoundException("Quiz", quiz_id)
    if current_user.role != UserRole.ADMIN and quiz.course.instructor_id != current_user.id:
        raise ForbiddenException("Unauthorized to modify this quiz")

    question = QuizQuestion(
        quiz_id=quiz.id,
        question_text=data.question_text,
        question_type=data.question_type,
        options=data.options,
        correct_answers=data.correct_answers,
        points=data.points,
        explanation=data.explanation,
        order_index=data.order_index,
    )
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


@router.post("/{quiz_id}/attempt", response_model=QuizAttemptResponse)
async def submit_quiz_attempt(
    quiz_id: int,
    data: QuizAttemptSubmit,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Submit quiz answers, compute score, and record attempt."""
    quiz = await db.scalar(
        select(Quiz).where(Quiz.id == quiz_id).options(selectinload(Quiz.questions))
    )
    if not quiz:
        raise NotFoundException("Quiz", quiz_id)

    total_points = sum(q.points for q in quiz.questions) or 1
    earned_points = 0.0

    # Calculate score
    for q in quiz.questions:
        user_answer = data.answers.get(str(q.id))
        if user_answer is None:
            user_answer = data.answers.get(q.id)

        if user_answer is not None:
            # Check correctness
            correct = q.correct_answers
            if isinstance(user_answer, list):
                if sorted([str(x) for x in user_answer]) == sorted([str(x) for x in correct]):
                    earned_points += q.points
            elif isinstance(user_answer, (str, int, bool)):
                if str(user_answer) in [str(x) for x in correct]:
                    earned_points += q.points

    score_pct = round((earned_points / total_points) * 100.0, 1)
    passed = score_pct >= quiz.passing_score
    now = datetime.now(timezone.utc)

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score_pct,
        passed=passed,
        answers_json=data.answers,
        started_at=now,
        completed_at=now,
    )
    db.add(attempt)
    await db.flush()
    await db.refresh(attempt)
    return attempt


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    quiz_id: int,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Get previous attempts of the current user for this quiz."""
    query = (
        select(QuizAttempt)
        .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())
