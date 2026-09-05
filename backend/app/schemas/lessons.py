from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.lesson import LessonType


class LessonBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    lesson_type: LessonType = LessonType.VIDEO
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_seconds: int = 0
    is_preview: bool = False
    order_index: int = Field(0, alias="order")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class LessonCreate(LessonBase):
    section_id: int


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    lesson_type: Optional[LessonType] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_preview: Optional[bool] = None
    order_index: Optional[int] = None


class LessonResponse(LessonBase):
    id: int
    section_id: int
    created_at: datetime
    is_completed: Optional[bool] = False
    last_position_seconds: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class LessonDetailResponse(LessonResponse):
    quiz_id: Optional[int] = None
    assignment_id: Optional[int] = None


class ProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    last_position_seconds: Optional[int] = 0


class LessonProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    is_completed: bool
    last_position_seconds: int
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
