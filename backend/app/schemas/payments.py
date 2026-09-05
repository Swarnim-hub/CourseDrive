from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.payment import PaymentStatus
from app.schemas.courses import CourseCardResponse


class CheckoutSessionCreate(BaseModel):
    course_id: int


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    stripe_payment_intent_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    course: Optional[CourseCardResponse] = None

    model_config = ConfigDict(from_attributes=True)
