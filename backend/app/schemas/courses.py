from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.course import CourseLevel
from app.schemas.users import UserResponse
from app.schemas.categories import CategoryResponse
from app.schemas.sections import SectionResponse


class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    description: str = Field(..., min_length=5)
    category_id: Optional[int] = None
    requirements: List[str] = []
    what_you_will_learn: List[str] = []
    level: CourseLevel = CourseLevel.ALL
    language: str = "English"
    price: float = Field(0.0, ge=0.0)
    is_free: bool = True
    promotional_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, v: Any) -> CourseLevel:
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ["all_levels", "all", "all levels"]:
                return CourseLevel.ALL
            elif v_lower in ["beginner", "intermediate", "advanced"]:
                return CourseLevel(v_lower)
        return CourseLevel.ALL

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    requirements: Optional[List[str]] = None
    what_you_will_learn: Optional[List[str]] = None
    level: Optional[CourseLevel] = None
    language: Optional[str] = None
    price: Optional[float] = Field(None, ge=0.0)
    is_free: Optional[bool] = None
    is_published: Optional[bool] = None
    promotional_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class CourseCardResponse(BaseModel):
    id: int
    title: str
    slug: str
    subtitle: Optional[str] = None
    thumbnail_url: Optional[str] = None
    level: CourseLevel
    price: float
    is_free: bool
    is_published: bool
    instructor: UserResponse
    category: Optional[CategoryResponse] = None
    rating: float = 0.0
    reviews_count: int = 0
    enrolled_count: int = 0
    total_duration_seconds: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseCardResponse):
    description: str
    requirements: List[str] = []
    what_you_will_learn: List[str] = []
    language: str
    promotional_video_url: Optional[str] = None
    sections: List[SectionResponse] = []
    is_enrolled: bool = False
    enrollment_status: Optional[str] = None
    progress_percentage: Optional[float] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    items: List[CourseCardResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
