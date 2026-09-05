from typing import List, Optional
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import CredentialsException, ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate bearer token and retrieve current user from database."""
    if not token:
        raise UnauthorizedException("Authentication token missing")
    
    try:
        payload = decode_token(token)
        user_id_str: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if user_id_str is None or token_type != "access":
            raise CredentialsException("Invalid token payload")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise CredentialsException("Could not validate token")

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise CredentialsException("User associated with this token does not exist")
    if not user.is_active:
        raise ForbiddenException("User account is inactive or disabled")

    return user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Retrieve current user if token is provided, otherwise None."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id_str: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        if user_id_str is None or token_type != "access":
            return None
        user_id = int(user_id_str)
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def require_roles(allowed_roles: List[UserRole]):
    """Dependency factory ensuring current user has one of allowed roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and current_user.role != UserRole.ADMIN:
            raise ForbiddenException(f"Access forbidden: requires one of {[r.value for r in allowed_roles]} roles")
        return current_user
    return role_checker


async def get_current_instructor(
    current_user: User = Depends(require_roles([UserRole.INSTRUCTOR, UserRole.ADMIN])),
) -> User:
    """Dependency ensuring user is instructor or admin."""
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency ensuring user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin privileges required")
    return current_user
