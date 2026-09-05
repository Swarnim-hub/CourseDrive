from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.assignment import SubmissionStatus
from app.schemas.users import UserResponse


class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    instructions: str = Field(..., min_length=5)
    max_score: int = Field(100, ge=1)
    due_date: Optional[datetime] = None


class AssignmentCreate(AssignmentBase):
    course_id: int
    lesson_id: Optional[int] = None


class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    instructions: Optional[str] = None
    max_score: Optional[int] = Field(None, ge=1)
    due_date: Optional[datetime] = None


class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int
    lesson_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentSubmissionCreate(BaseModel):
    submission_text: Optional[str] = None
    file_url: Optional[str] = None


class AssignmentSubmissionGrade(BaseModel):
    score: float = Field(..., ge=0)
    feedback: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.GRADED


class AssignmentSubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    user: Optional[UserResponse] = None
    submission_text: Optional[str] = None
    file_url: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    status: SubmissionStatus
    submitted_at: datetime
    graded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
