import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.models.course import Course
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.services.enrollment_service import enrollment_service

logger = logging.getLogger(__name__)

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    async def create_checkout_session(
        self,
        db: AsyncSession,
        user: User,
        course_id: int,
    ) -> Dict[str, str]:
        """Create Stripe Checkout Session for course purchase."""
        course = await db.scalar(select(Course).where(Course.id == course_id))
        if not course:
            raise NotFoundException("Course", course_id)

        if course.is_free or course.price <= 0:
            # Direct enrollment for free courses
            await enrollment_service.enroll_student(db, user.id, course_id)
            return {
                "checkout_url": f"{settings.FRONTEND_URL}/learn/{course.slug}",
                "session_id": "free_enrollment",
            }

        unit_amount = int(course.price * 100)

        # In case mock/test placeholder keys are present, provide a mock checkout or real stripe session
        if settings.STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
            # Create a pending payment record and provide simulated redirect
            payment = Payment(
                user_id=user.id,
                course_id=course_id,
                stripe_payment_intent_id=f"pi_mock_{course_id}_{user.id}",
                stripe_session_id=f"cs_mock_{course_id}_{user.id}",
                amount=float(course.price),
                currency=settings.STRIPE_CURRENCY,
                status=PaymentStatus.PENDING,
            )
            db.add(payment)
            await db.flush()

            return {
                "checkout_url": f"{settings.FRONTEND_URL}/checkout/success?session_id={payment.stripe_session_id}&course_id={course_id}",
                "session_id": payment.stripe_session_id,
            }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=user.email,
                client_reference_id=str(user.id),
                line_items=[
                    {
                        "price_data": {
                            "currency": settings.STRIPE_CURRENCY,
                            "product_data": {
                                "name": course.title,
                                "description": course.subtitle or f"Enrollment in {course.title}",
                                "images": [course.thumbnail_url] if course.thumbnail_url else [],
                            },
                            "unit_amount": unit_amount,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                metadata={
                    "user_id": str(user.id),
                    "course_id": str(course.id),
                },
                success_url=f"{settings.FRONTEND_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&course_id={course_id}",
                cancel_url=f"{settings.FRONTEND_URL}/courses/{course.slug}?canceled=true",
            )

            # Record pending payment
            payment = Payment(
                user_id=user.id,
                course_id=course_id,
                stripe_session_id=session.id,
                amount=float(course.price),
                currency=settings.STRIPE_CURRENCY,
                status=PaymentStatus.PENDING,
            )
            db.add(payment)
            await db.flush()

            return {
                "checkout_url": session.url,
                "session_id": session.id,
            }
        except Exception as e:
            logger.error(f"Stripe session creation error: {e}")
            raise BadRequestException(f"Failed to initiate payment session: {str(e)}")

    async def handle_checkout_completed(self, db: AsyncSession, session_data: Dict[str, Any]) -> bool:
        """Process successful checkout session (e.g. from webhook or confirmation)."""
        session_id = session_data.get("id")
        metadata = session_data.get("metadata", {})
        user_id = int(metadata.get("user_id") or session_data.get("client_reference_id", 0))
        course_id = int(metadata.get("course_id", 0))

        if not user_id or not course_id:
            logger.warning("Missing user_id or course_id in stripe session data")
            return False

        # Find payment record
        query = select(Payment).where(
            (Payment.stripe_session_id == session_id) |
            ((Payment.user_id == user_id) & (Payment.course_id == course_id) & (Payment.status == PaymentStatus.PENDING))
        )
        payment = await db.scalar(query)
        if payment:
            payment.status = PaymentStatus.SUCCEEDED
            payment.stripe_payment_intent_id = session_data.get("payment_intent")
            await db.flush()

        # Enroll student in course
        await enrollment_service.enroll_student(db, user_id, course_id)
        return True


payment_service = PaymentService()
