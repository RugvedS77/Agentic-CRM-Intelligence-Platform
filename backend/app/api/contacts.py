from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.contact_model import Contact
from app.models.audit_log_model import AuditLog

router = APIRouter(prefix="/contacts", tags=["Contacts"])

class UpdateStatusPayload(BaseModel):
    status: str
    user_id: str

@router.get("/{email}")
def get_contact(email: str, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact record not found")
    return contact

@router.patch("/{email}/status")
def update_contact_status(email: str, payload: UpdateStatusPayload, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact record not found")
    
    old_status = contact.status
    db.query(Contact).filter(Contact.email == email).update({"status": payload.status})
    
    # Log an explicit tracking entry inside our new audit logs
    audit = AuditLog(
        entity_type="contact",
        entity_id=email,
        action="STATUS_UPDATE",
        performed_by=payload.user_id,
        diff={"old_status": old_status, "new_status": payload.status}
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "updated_to": payload.status}