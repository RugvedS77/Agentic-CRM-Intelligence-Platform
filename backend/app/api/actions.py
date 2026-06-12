from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.action_model import Action
from app.models.email_model import Email
from app.models.audit_log_model import AuditLog

router = APIRouter(tags=["Actions"])

class RespondPayload(BaseModel):
    reply_body: str
    user_id: str

class DraftUpdatePayload(BaseModel):
    proposed_content: str

class ApprovePayload(BaseModel):
    user_id: str

@router.post("/respond/{email_id}")
def send_manual_reply(email_id: str, payload: RespondPayload, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.message_id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.status = "Replied"
    
    # Log the manual response action
    action = Action(
        email_id=email_id,
        action_type="Manual-Reply",
        proposed_content=payload.reply_body,
        is_approved=True,
        approved_by=payload.user_id
    )
    db.add(action)
    db.commit()
    
    return {"status": "success", "message": "Reply sent and status updated."}

@router.patch("/drafts/{draft_id}")
def update_draft(draft_id: int, payload: DraftUpdatePayload, db: Session = Depends(get_db)):
    draft = db.query(Action).filter(Action.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    draft.proposed_content = payload.proposed_content
    db.commit()
    return {"status": "success", "message": "Draft updated."}

@router.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: int, payload: ApprovePayload, db: Session = Depends(get_db)):
    draft = db.query(Action).filter(Action.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    draft.is_approved = True
    draft.approved_by = payload.user_id
    
    # Update parent email status
    email = db.query(Email).filter(Email.message_id == draft.email_id).first()
    if email:
        email.status = "Replied"
    
    # Trigger audit log entry
    audit = AuditLog(
        entity_type="draft",
        entity_id=str(draft_id),
        action="DRAFT_APPROVED",
        performed_by=payload.user_id,
        diff={"action": "Sent auto-reply draft to customer"}
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "message": "Draft approved and sent."}


class BulkActionPayload(BaseModel):
    email_ids: list
    user_id: str


@router.post("/bulk/archive")
def bulk_archive(payload: BulkActionPayload, db: Session = Depends(get_db)):
    for email_id in payload.email_ids:
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            email.status = "Archived"
            audit = AuditLog(
                entity_type="email",
                entity_id=str(email_id),
                action="BULK_ARCHIVE",
                performed_by=payload.user_id
            )
            db.add(audit)
    db.commit()
    return {"status": "success", "message": f"Archived {len(payload.email_ids)} emails"}


@router.post("/bulk/spam")
def bulk_spam(payload: BulkActionPayload, db: Session = Depends(get_db)):
    for email_id in payload.email_ids:
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            email.category = "Spam"
            email.status = "Filtered"
            audit = AuditLog(
                entity_type="email",
                entity_id=str(email_id),
                action="BULK_SPAM",
                performed_by=payload.user_id
            )
            db.add(audit)
    db.commit()
    return {"status": "success", "message": f"Marked {len(payload.email_ids)} emails as spam"}


@router.post("/bulk/assign")
def bulk_assign(payload: BulkActionPayload, db: Session = Depends(get_db)):
    for email_id in payload.email_ids:
        email = db.query(Email).filter(Email.id == email_id).first()
        if email:
            email.status = "Assigned"
            audit = AuditLog(
                entity_type="email",
                entity_id=str(email_id),
                action="BULK_ASSIGN",
                performed_by=payload.user_id
            )
            db.add(audit)
    db.commit()
    return {"status": "success", "message": f"Assigned {len(payload.email_ids)} emails"}