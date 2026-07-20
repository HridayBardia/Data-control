from uuid import UUID
from typing import Generator
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_token
from app.models.entities import User, Organization
from app.schemas.auth import TokenPayload

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Extracts the user credentials from the JWT bearer token, checks database
    validation, and ensures the user exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access_token":
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
        user_uuid = UUID(token_data.sub) if isinstance(token_data.sub, str) else token_data.sub
    except (JWTError, ValueError):
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Validates that the user account is marked active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def get_current_active_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Restricts access to system admin and organization admin roles.
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_user

def get_current_tenant_org(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Validates and fetches the organization tenant associated with the user.
    """
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org or not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Associated organization is inactive or missing."
        )
    return org
