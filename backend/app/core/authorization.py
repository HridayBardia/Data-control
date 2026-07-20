import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Role(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    MANAGER = "MANAGER"
    DEVELOPER = "DEVELOPER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
    GUEST = "GUEST"


ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 100,
    Role.ORG_ADMIN: 80,
    Role.MANAGER: 60,
    Role.DEVELOPER: 40,
    Role.MEMBER: 20,
    Role.VIEWER: 10,
    Role.GUEST: 0
}


class AuthContext(BaseModel):
    user_id: str
    organization_id: str
    role: Role
    department: Optional[str] = None
    projects: List[str] = []
    permissions: List[str] = []


class ABACPolicy(BaseModel):
    id: str
    name: str
    action: str  # e.g., "read", "write", "delete", "export"
    resource_type: str  # e.g., "document", "connector", "audit_log"
    allowed_roles: List[Role] = []
    required_department: Optional[str] = None
    required_classification: Optional[str] = None  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED


class PermissionEvaluator:
    """Enterprise Policy Engine combining RBAC role hierarchies with ABAC condition rules."""

    @staticmethod
    def is_role_sufficient(user_role: Role, required_role: Role) -> bool:
        return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)

    @classmethod
    def evaluate(
        cls,
        context: AuthContext,
        action: str,
        resource_type: str,
        resource_org_id: str,
        resource_metadata: Optional[Dict[str, Any]] = None,
        policy: Optional[ABACPolicy] = None
    ) -> Tuple[bool, str]:
        # 1. Multi-Tenant Isolation Check
        if context.organization_id != resource_org_id and context.role != Role.SUPER_ADMIN:
            return False, "Tenant mismatch: Unauthorized cross-organization resource access"

        # 2. Super Admin override
        if context.role == Role.SUPER_ADMIN or context.role == Role.ORG_ADMIN:
            return True, "Granted by administrative role"

        # 3. Policy Evaluation
        if policy:
            if policy.allowed_roles and context.role not in policy.allowed_roles:
                return False, f"Role {context.role} not permitted by policy {policy.name}"

            if policy.required_department and context.department != policy.required_department:
                return False, f"Department mismatch. Required: {policy.required_department}"

        # 4. Attribute Based Classification Filter
        if resource_metadata:
            classification = resource_metadata.get("classification", "INTERNAL")
            if classification == "RESTRICTED" and not cls.is_role_sufficient(context.role, Role.MANAGER):
                return False, "RESTRICTED classification requires MANAGER role or above"

        # 5. Default Permission Match
        required_perm = f"{action}:{resource_type}"
        if context.permissions and required_perm not in context.permissions:
            if not cls.is_role_sufficient(context.role, Role.MEMBER):
                return False, f"Insufficient permissions for action {action} on {resource_type}"

        return True, "Access granted"
