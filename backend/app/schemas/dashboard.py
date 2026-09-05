from typing import Dict, List, Optional
from pydantic import BaseModel
from app.schemas.courses import CourseCardResponse
from app.schemas.enrollments import EnrollmentDetailResponse
from app.schemas.certificates import CertificateResponse


class StudentDashboardResponse(BaseModel):
    enrolled_courses: List[EnrollmentDetailResponse]
    completed_courses: List[EnrollmentDetailResponse]
    certificates: List[CertificateResponse]
    total_learning_hours: float
    quizzes_passed: int
    assignments_completed: int


class InstructorDashboardResponse(BaseModel):
    total_students: int
    total_courses: int
    total_revenue: float
    average_rating: float
    recent_enrollments: List[dict]
    popular_courses: List[CourseCardResponse]


class InstructorAnalyticsResponse(BaseModel):
    monthly_revenue: Dict[str, float]
    monthly_enrollments: Dict[str, int]
    course_ratings_breakdown: Dict[str, float]
    completion_rates: Dict[str, float]
