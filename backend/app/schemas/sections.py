from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.lessons import LessonResponse


class SectionBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    order_index: int = Field(0, alias="order")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class SectionCreate(SectionBase):
    course_id: Optional[int] = None


class SectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    order_index: Optional[int] = None


class SectionResponse(SectionBase):
    id: int
    course_id: int
    created_at: datetime
    lessons: List[LessonResponse] = []

    model_config = ConfigDict(from_attributes=True)
