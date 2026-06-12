from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.email_model import Email

router = APIRouter(prefix="/inbox", tags=["Inbox"])

@router.get("/")
def get_inbox_emails(db: Session = Depends(get_db)):
    emails = (
        db.query(Email)
        .order_by(Email.timestamp.desc())
        .limit(100)
        .all()
    )
    
    return [
        {
            "id": e.id,
            "message_id": e.message_id,
            "thread_id": e.thread_id,
            "sender": e.sender,
            "subject": e.subject,
            "timestamp": e.timestamp,
            "category": e.category,
            "sentiment": e.sentiment,
            "urgency": e.urgency,
            "status": e.status,
            "requires_human": e.requires_human
        }
        for e in emails
    ]