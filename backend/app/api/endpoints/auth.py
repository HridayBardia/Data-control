from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.core import security
from app.core.config import settings
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    OrganizationCreate,
    OrganizationResponse,
    Token
)
from app.services.auth import AuthService
from app.services.audit import AuditService
from app.models.entities import User

router = APIRouter()

@router.post("/register/organization", response_model=OrganizationResponse)
def register_organization(org_in: OrganizationCreate, db: Session = Depends(get_db)):
    """
    Bootstrap a new enterprise tenant.
    """
    existing_org = AuthService.get_org_by_slug(db, org_in.slug)
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this slug already exists."
        )
    return AuthService.create_organization(db, org_in)


@router.post("/register/user", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a user under a specific enterprise tenant slug.
    """
    existing_user = AuthService.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered."
        )
    try:
        return AuthService.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, retrieve access and refresh tokens.
    """
    user = AuthService.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user account"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(subject=user.id)

    # Log successful login to Audit logs
    AuditService.create_log(
        db=db,
        organization_id=user.organization_id,
        user_id=user.id,
        action="USER_LOGIN_SUCCESSFUL",
        payload={"email": user.email}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current logged in user details.
    """
    return current_user
