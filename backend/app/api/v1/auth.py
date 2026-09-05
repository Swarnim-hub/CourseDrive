from fastapi import APIRouter, status
from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BadRequestException
from app.core.security import get_password_hash, verify_password
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    SendOTPRequest,
    TokenResponse,
    VerifyOTPRequest,
)
from app.schemas.users import UserResponse
from app.services.auth_service import auth_service
from app.services.otp_service import otp_service
from app.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: SessionDep):
    """Register a new user account."""
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: SessionDep):
    """Log in with email and password."""
    return await auth_service.authenticate_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: SessionDep):
    """Refresh access token with a valid refresh token."""
    return await auth_service.refresh_access_token(db, data.refresh_token)


@router.post("/send-otp")
async def send_otp(data: SendOTPRequest):
    """Generate and send OTP to the specified email."""
    otp = otp_service.generate_otp()
    await otp_service.store_otp(data.email, otp)
    await email_service.send_otp_email(data.email, otp)
    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
async def verify_otp(data: VerifyOTPRequest, db: SessionDep):
    """Verify OTP code and authenticate user."""
    return await auth_service.verify_email_otp(db, data.email, data.otp_code)


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: SessionDep):
    """Trigger password reset OTP."""
    await auth_service.send_password_reset_otp(db, data.email)
    return {"message": "If this email is registered, a password reset code has been sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: SessionDep):
    """Confirm password reset using OTP and new password."""
    await auth_service.confirm_password_reset(db, data.email, data.otp_code, data.new_password)
    return {"message": "Password has been successfully updated"}


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, current_user: CurrentUserDep, db: SessionDep):
    """Change password for the logged-in user."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise BadRequestException("Current password does not match")
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.flush()
    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentUserDep):
    """Retrieve logged-in user profile."""
    return current_user
