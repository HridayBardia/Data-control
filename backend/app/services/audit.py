from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.entities import AuditLog

class AuditService:
    @staticmethod
    def create_log(
        db: Session,
        organization_id: UUID,
        action: str,
        user_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Creates an immutable, chain-hashed audit log entry for tamper-resistance.
        """
        # Fetch last log hash to construct the chain
        last_log = (
            db.query(AuditLog)
            .filter(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.desc())
            .first()
        )
        prev_hash = last_log.row_hash if last_log else "genesis_salt_project_atlas_2026"

        # Construct log instance with explicit microsecond timestamp for ordering
        log_entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            payload=payload or {},
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(log_entry)
        db.flush()  # Gen ID and set database-level defaults

        # Compute cryptographic hash for tamper resistance
        hasher = hashlib.sha256()
        payload_data = log_entry.payload if isinstance(log_entry.payload, dict) else (json.loads(log_entry.payload) if log_entry.payload else {})
        serialized_fields = {
            "id": str(log_entry.id),
            "organization_id": str(log_entry.organization_id),
            "user_id": str(log_entry.user_id) if log_entry.user_id else "",
            "action": log_entry.action,
            "payload": json.dumps(payload_data, sort_keys=True),
            "prev_hash": prev_hash
        }
        
        hasher.update(json.dumps(serialized_fields, sort_keys=True).encode("utf-8"))
        log_entry.row_hash = hasher.hexdigest()
        
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def verify_chain(db: Session, organization_id: UUID) -> bool:
        """
        Validates the integrity of the audit log chain for an organization.
        Returns True if the chain is intact, False if tampering is detected.
        """
        logs = (
            db.query(AuditLog)
            .filter(AuditLog.organization_id == organization_id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )
        
        prev_hash = "genesis_salt_project_atlas_2026"
        for log in logs:
            hasher = hashlib.sha256()
            payload_data = log.payload if isinstance(log.payload, dict) else (json.loads(log.payload) if log.payload else {})
            serialized_fields = {
                "id": str(log.id),
                "organization_id": str(log.organization_id),
                "user_id": str(log.user_id) if log.user_id else "",
                "action": log.action,
                "payload": json.dumps(payload_data, sort_keys=True),
                "prev_hash": prev_hash
            }
            hasher.update(json.dumps(serialized_fields, sort_keys=True).encode("utf-8"))
            expected_hash = hasher.hexdigest()
            
            if log.row_hash != expected_hash:
                # Tampering detected
                return False
            prev_hash = log.row_hash
            
        return True
