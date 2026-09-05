from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.courses import CourseCardResponse
from app.schemas.users import UserResponse


class CertificateResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    certificate_number: str
    issue_date: datetime
    pdf_url: Optional[str] = None
    course: Optional[CourseCardResponse] = None
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CertificateVerificationResponse(BaseModel):
    valid: bool
    certificate_number: str
    student_name: Optional[str] = None
    course_title: Optional[str] = None
    instructor_name: Optional[str] = None
    issue_date: Optional[datetime] = None
    pdf_url: Optional[str] = None
