from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    headline: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    headline: Optional[str] = None


class UserAdminUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    bio: Optional[str] = None
    headline: Optional[str] = None


class UserProfileResponse(UserResponse):
    enrolled_courses_count: int = 0
    completed_courses_count: int = 0
    certificates_count: int = 0
    instructed_courses_count: Optional[int] = None
