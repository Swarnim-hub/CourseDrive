from typing import Annotated, Optional
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.permissions import (
    get_current_user,
    get_optional_current_user,
    get_current_instructor,
    get_current_admin,
    require_roles,
)
from app.models.user import User, UserRole

# Reusable typed dependencies
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[User], Depends(get_optional_current_user)]
InstructorUserDep = Annotated[User, Depends(get_current_instructor)]
AdminUserDep = Annotated[User, Depends(get_current_admin)]


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
