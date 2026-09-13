import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException, UnauthorizedException
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (FOUNDER or ADMIN) with bcrypt hashed password and issue JWT token.
    """
    # Check if email is already registered
    existing_res = db.execute(select(User).filter(User.email == payload.email.lower()))
    if existing_res.scalars().first():
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"User with email '{payload.email}' already exists"
        )

    # Validate role
    user_role = (payload.role or "FOUNDER").upper()
    if user_role not in ("FOUNDER", "ADMIN"):
        user_role = "FOUNDER"

    hashed_pwd = hash_password(payload.password)
    new_user = User(
        id=str(uuid.uuid4()),
        email=payload.email.lower(),
        hashed_password=hashed_pwd,
        role=user_role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.id, "email": new_user.email, "role": new_user.role})
    user_resp = UserResponse.model_validate(new_user)
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user credentials and issue a signed JWT access token.
    """
    result = db.execute(select(User).filter(User.email == payload.email.lower()))
    user = result.scalars().first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException(message="Invalid email or password")

    token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    user_resp = UserResponse.model_validate(user)
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieve authenticated user profile. Requires Bearer token.
    """
    return UserResponse.model_validate(current_user)
