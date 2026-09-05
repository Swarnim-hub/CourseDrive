from typing import List
import stripe
from fastapi import APIRouter, Header, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, SessionDep
from app.config import settings
from app.core.exceptions import BadRequestException
from app.models.course import Course
from app.models.payment import Payment, PaymentStatus
from app.schemas.courses import CourseCardResponse
from app.schemas.payments import CheckoutSessionCreate, CheckoutSessionResponse, PaymentResponse
from app.schemas.users import UserResponse
from app.services.course_service import course_service
from app.services.enrollment_service import enrollment_service
from app.services.payment_service import payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    data: CheckoutSessionCreate,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Create Stripe Checkout Session for purchasing a course."""
    result = await payment_service.create_checkout_session(db, current_user, data.course_id)
    return result


@router.post("/confirm-mock")
async def confirm_mock_payment(
    session_id: str,
    course_id: int,
    current_user: CurrentUserDep,
    db: SessionDep,
):
    """Local development/testing mock payment confirmation."""
    payment = await db.scalar(
        select(Payment).where(
            Payment.stripe_session_id == session_id,
            Payment.user_id == current_user.id,
        )
    )
    if payment:
        payment.status = PaymentStatus.SUCCEEDED
        await db.flush()

    await enrollment_service.enroll_student(db, current_user.id, course_id)
    return {"status": "succeeded", "message": "Successfully enrolled via dev mock payment"}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: SessionDep, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """Stripe webhook listener for completed payments."""
    payload = await request.body()
    try:
        if settings.STRIPE_WEBHOOK_SECRET and not settings.STRIPE_WEBHOOK_SECRET.startswith("whsec_placeholder"):
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            import json
            event = json.loads(payload.decode("utf-8"))
    except Exception as e:
        raise BadRequestException(f"Webhook signature error: {str(e)}")

    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        session_obj = event.get("data", {}).get("object", {})
        await payment_service.handle_checkout_completed(db, session_obj)

    return {"status": "success"}


@router.get("/my", response_model=List[PaymentResponse])
async def get_my_payments(current_user: CurrentUserDep, db: SessionDep):
    """Get payment history for the logged-in user."""
    query = (
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .options(
            selectinload(Payment.course).selectinload(Course.instructor),
            selectinload(Payment.course).selectinload(Course.category),
        )
        .order_by(Payment.created_at.desc())
    )
    result = await db.execute(query)
    payments = list(result.scalars().all())

    response: List[PaymentResponse] = []
    for p in payments:
        card = None
        if p.course:
            stats = await course_service.get_course_stats(db, p.course.id)
            card = CourseCardResponse(
                id=p.course.id,
                title=p.course.title,
                slug=p.course.slug,
                subtitle=p.course.subtitle,
                thumbnail_url=p.course.thumbnail_url,
                level=p.course.level,
                price=float(p.course.price),
                is_free=p.course.is_free,
                is_published=p.course.is_published,
                instructor=UserResponse.model_validate(p.course.instructor),
                category=p.course.category,
                rating=stats["rating"],
                reviews_count=stats["reviews_count"],
                enrolled_count=stats["enrolled_count"],
                total_duration_seconds=p.course.total_duration_seconds,
                created_at=p.course.created_at,
            )
        response.append(PaymentResponse(
            id=p.id,
            user_id=p.user_id,
            course_id=p.course_id,
            stripe_payment_intent_id=p.stripe_payment_intent_id,
            stripe_session_id=p.stripe_session_id,
            amount=float(p.amount),
            currency=p.currency,
            status=p.status,
            created_at=p.created_at,
            course=card,
        ))
    return response
