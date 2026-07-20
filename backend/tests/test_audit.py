import uuid
from sqlalchemy.orm import Session
from app.services.audit import AuditService
from app.models.entities import AuditLog, Organization

def test_audit_log_cryptographic_chain(db: Session):
    # 1. Create a dummy organization to scope logs
    org = Organization(name="Audit Test Org", slug="audit-test-org")
    db.add(org)
    db.commit()
    db.refresh(org)

    # 2. Append multiple logs
    log1 = AuditService.create_log(
        db=db,
        organization_id=org.id,
        action="USER_LOGIN",
        payload={"username": "user1@test.com"}
    )
    
    log2 = AuditService.create_log(
        db=db,
        organization_id=org.id,
        action="DOCUMENT_VIEWED",
        payload={"doc_id": str(uuid.uuid4())}
    )

    log3 = AuditService.create_log(
        db=db,
        organization_id=org.id,
        action="USER_LOGOUT",
        payload={"username": "user1@test.com"}
    )

    # 3. Verify the chain is intact
    assert AuditService.verify_chain(db, org.id) is True

    # 4. Simulate tampering (modify log2's payload without updating hash)
    log2.payload = {"doc_id": str(uuid.uuid4()), "hacked": True}
    db.add(log2)
    db.commit()

    # 5. Verify the chain now detects the tampering
    assert AuditService.verify_chain(db, org.id) is False
