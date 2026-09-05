from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enrollment import EnrollmentStatus
from app.schemas.courses import CourseCardResponse


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float
    status: EnrollmentStatus

    model_config = ConfigDict(from_attributes=True)


class EnrollmentDetailResponse(EnrollmentResponse):
    course: CourseCardResponse
