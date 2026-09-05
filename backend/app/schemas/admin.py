from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from app.schemas.users import UserResponse


class AdminStatsResponse(BaseModel):
    total_users: int
    total_instructors: int
    total_students: int
    total_courses: int
    published_courses: int
    total_enrollments: int
    total_revenue: float
    total_certificates: int


class AdminUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class SystemHealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    timestamp: datetime
