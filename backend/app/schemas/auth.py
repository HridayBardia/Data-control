from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the organization")
    slug: str = Field(..., max_length=255, description="URL slug unique identifier")

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "MEMBER"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    organization_slug: str

class UserResponse(UserBase):
    id: UUID
    organization_id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[float] = None
    type: Optional[str] = None
