from datetime import datetime, timezone
from typing import Dict, List
from fastapi import APIRouter, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.review import Review
from app.models.user import UserRole
from app.schemas.reviews import (
    CourseReviewsSummaryResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from app.schemas.users import UserResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/course/{course_id}", response_model=CourseReviewsSummaryResponse)
async def get_course_reviews(course_id: int, db: SessionDep):
    """Retrieve all reviews and rating breakdown for a course."""
    query = (
        select(Review)
        .where(Review.course_id == course_id)
        .options(selectinload(Review.user))
        .order_by(Review.created_at.desc())
    )
    result = await db.execute(query)
    reviews = list(result.scalars().all())

    total = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total, 1) if total > 0 else 0.0

    distribution: Dict[int, int] = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        distribution[r.rating] = distribution.get(r.rating, 0) + 1

    return CourseReviewsSummaryResponse(
        average_rating=avg_rating,
        total_reviews=total,
        rating_distribution=distribution,
        reviews=[
            ReviewResponse(
                id=r.id,
                user_id=r.user_id,
                course_id=r.course_id,
                rating=r.rating,
                comment=r.comment,
                created_at=r.created_at,
                updated_at=r.updated_at,
                user=UserResponse.model_validate(r.user) if r.user else None,
            )
            for r in reviews
        ],
    )


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(data: ReviewCreate, current_user: CurrentUserDep, db: SessionDep):
    """Add a review for an enrolled course."""
    # Verify enrollment
    enrollment = await db.scalar(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == data.course_id,
            Enrollment.status.in_([EnrollmentStatus.ACTIVE, EnrollmentStatus.COMPLETED]),
        )
    )
    if not enrollment:
        raise BadRequestException("You must be enrolled in this course to leave a review")

    # Check if already reviewed
    existing = await db.scalar(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.course_id == data.course_id,
        )
    )
    if existing:
        raise BadRequestException("You have already reviewed this course. Use PUT to update your review.")

    review = Review(
        user_id=current_user.id,
        course_id=data.course_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        course_id=review.course_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user=UserResponse.model_validate(current_user),
    )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: int, data: ReviewUpdate, current_user: CurrentUserDep, db: SessionDep):
    """Update user's review."""
    review = await db.scalar(select(Review).where(Review.id == review_id))
    if not review:
        raise NotFoundException("Review", review_id)
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Unauthorized to modify this review")

    if data.rating is not None:
        review.rating = data.rating
    if data.comment is not None:
        review.comment = data.comment
    review.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        course_id=review.course_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
        user=UserResponse.model_validate(current_user),
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: int, current_user: CurrentUserDep, db: SessionDep):
    """Delete a review."""
    review = await db.scalar(select(Review).where(Review.id == review_id))
    if not review:
        raise NotFoundException("Review", review_id)
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Unauthorized to delete this review")

    await db.delete(review)
    await db.flush()
