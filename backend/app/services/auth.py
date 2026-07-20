from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.models.entities import User, Organization
from app.schemas.auth import UserCreate, OrganizationCreate
from app.services.audit import AuditService

class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_org_by_slug(db: Session, slug: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.slug == slug).first()

    @staticmethod
    def create_organization(db: Session, org_in: OrganizationCreate) -> Organization:
        db_org = Organization(
            name=org_in.name,
            slug=org_in.slug
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        
        # Log system event
        AuditService.create_log(
            db=db,
            organization_id=db_org.id,
            action="ORGANIZATION_CREATED",
            payload={"org_name": db_org.name, "org_slug": db_org.slug}
        )
        return db_org

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        # Check org existence
        org = AuthService.get_org_by_slug(db, user_in.organization_slug)
        if not org:
            raise ValueError(f"Organization with slug '{user_in.organization_slug}' does not exist.")
            
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role,
            organization_id=org.id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Log system event
        AuditService.create_log(
            db=db,
            organization_id=org.id,
            user_id=db_user.id,
            action="USER_REGISTERED",
            payload={"email": db_user.email, "role": db_user.role}
        )
        return db_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
