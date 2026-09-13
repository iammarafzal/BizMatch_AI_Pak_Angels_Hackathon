from typing import Optional, Callable
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.auth import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extracts Bearer token from Authorization header, validates JWT claims,
    and returns the authenticated User instance from database.
    Raises 401 Unauthorized if token is missing, expired, or invalid.
    """
    if not token:
        raise UnauthorizedException(
            message="Authentication required",
            details="Missing Bearer token in Authorization header"
        )

    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")
    
    if not user_id:
        raise UnauthorizedException(
            message="Invalid token payload",
            details="Subject claim 'sub' missing from token payload"
        )

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise UnauthorizedException(
            message="User profile not found",
            details=f"User ID '{user_id}' does not exist"
        )

    return user

def require_role(required_role: str) -> Callable:
    """
    Dependency factory enforcing Role-Based Access Control (RBAC).
    Raises 403 Forbidden if current user role does not match required_role.
    ADMIN role bypasses restriction and has global access.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == "ADMIN":
            return current_user
        if current_user.role != required_role:
            raise ForbiddenException(
                message="Operation forbidden",
                details=f"Role '{required_role}' required. Current role: '{current_user.role}'."
            )
        return current_user
    return role_checker
