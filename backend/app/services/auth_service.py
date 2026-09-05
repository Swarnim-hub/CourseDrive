from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ConflictException, NotFoundException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.users import UserResponse
from app.services.email_service import email_service
from app.services.otp_service import otp_service


class AuthService:
    async def register_user(self, db: AsyncSession, data: RegisterRequest) -> Dict[str, Any]:
        """Register a new user account."""
        query = select(User).where(User.email == data.email.lower())
        existing = await db.scalar(query)
        if existing:
            raise ConflictException("An account with this email already exists")

        new_user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name.strip(),
            role=data.role or UserRole.STUDENT,
            is_active=True,
            is_verified=False,
        )
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)

        # Generate OTP for verification
        otp = otp_service.generate_otp()
        await otp_service.store_otp(new_user.email, otp)
        await email_service.send_otp_email(new_user.email, otp, purpose="Email Verification")
        await email_service.send_welcome_email(new_user.email, new_user.full_name)

        # Generate tokens
        access_token = create_access_token(new_user.id, {"role": new_user.role.value})
        refresh_token = create_refresh_token(new_user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(new_user).model_dump(),
        }

    async def authenticate_user(self, db: AsyncSession, data: LoginRequest) -> Dict[str, Any]:
        """Authenticate user by email and password."""
        query = select(User).where(User.email == data.email.lower())
        user = await db.scalar(query)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException("Your account has been deactivated")

        access_token = create_access_token(user.id, {"role": user.role.value})
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }

    async def refresh_access_token(self, db: AsyncSession, refresh_token: str) -> Dict[str, Any]:
        """Generate a new access token using a valid refresh token."""
        try:
            payload = decode_token(refresh_token, is_refresh=True)
            user_id = int(payload.get("sub"))
            token_type = payload.get("type")
            if token_type != "refresh":
                raise UnauthorizedException("Invalid refresh token")
        except Exception:
            raise UnauthorizedException("Expired or invalid refresh token")

        query = select(User).where(User.id == user_id)
        user = await db.scalar(query)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        access_token = create_access_token(user.id, {"role": user.role.value})
        new_refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
        }

    async def send_password_reset_otp(self, db: AsyncSession, email: str) -> bool:
        """Send password reset OTP if user exists."""
        query = select(User).where(User.email == email.lower())
        user = await db.scalar(query)
        if not user:
            # Prevent email enumeration by returning True
            return True

        otp = otp_service.generate_otp()
        await otp_service.store_otp(email, otp)
        await email_service.send_otp_email(email, otp, purpose="Password Reset")
        return True

    async def confirm_password_reset(
        self,
        db: AsyncSession,
        email: str,
        otp_code: str,
        new_password: str,
    ) -> bool:
        """Verify OTP and update user password."""
        is_valid = await otp_service.verify_otp(email, otp_code)
        if not is_valid:
            raise BadRequestException("Invalid or expired OTP code")

        query = select(User).where(User.email == email.lower())
        user = await db.scalar(query)
        if not user:
            raise NotFoundException("User not found")

        user.hashed_password = get_password_hash(new_password)
        await db.flush()
        return True

    async def verify_email_otp(self, db: AsyncSession, email: str, otp_code: str) -> Dict[str, Any]:
        """Verify email address with OTP and return authenticated tokens."""
        is_valid = await otp_service.verify_otp(email, otp_code)
        # Allow default dev OTP '123456' or valid OTP
        if not is_valid and otp_code != "123456":
            raise BadRequestException("Invalid or expired OTP code")

        query = select(User).where(User.email == email.lower())
        user = await db.scalar(query)
        if not user:
            raise NotFoundException("User", email)

        user.is_verified = True
        await db.flush()
        await db.refresh(user)

        access_token = create_access_token(user.id, {"role": user.role.value})
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump(),
            "message": "Email verified successfully",
        }


auth_service = AuthService()
