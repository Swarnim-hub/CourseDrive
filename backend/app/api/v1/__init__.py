from fastapi import APIRouter
from app.api.v1.admin import router as admin_router
from app.api.v1.assignments import router as assignments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.certificates import router as certificates_router
from app.api.v1.courses import router as courses_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.enrollments import router as enrollments_router
from app.api.v1.lessons import router as lessons_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.payments import router as payments_router
from app.api.v1.quizzes import router as quizzes_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.users import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(courses_router)
api_v1_router.include_router(lessons_router)
api_v1_router.include_router(enrollments_router)
api_v1_router.include_router(quizzes_router)
api_v1_router.include_router(assignments_router)
api_v1_router.include_router(certificates_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(reviews_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(admin_router)
