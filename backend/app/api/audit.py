from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit_log_model import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/{entity_type}/{entity_id}")
def get_audit_trail(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    return logs