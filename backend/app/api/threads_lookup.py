from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.thread_model import Thread
from app.models.email_model import Email

router = APIRouter(tags=["Threads"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/threads/{contact_email}")
def get_threads_by_contact(contact_email: str, db: Session = Depends(get_db)):
    threads = (
        db.query(Thread)
        .filter(Thread.participants.contains(contact_email))
        .order_by(Thread.updated_at.desc())
        .all()
    )

    result = []
    for thread in threads:
        emails = (
            db.query(Email)
            .filter(Email.thread_id == thread.thread_id)
            .order_by(Email.timestamp.asc())
            .all()
        )
        result.append(
            {
                "thread_id": thread.thread_id,
                "subject": thread.subject,
                "participants": thread.participants,
                "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
                "emails": [
                    {
                        "message_id": e.message_id,
                        "sender": e.sender,
                        "subject": e.subject,
                        "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                        "category": e.category,
                        "sentiment": e.sentiment,
                        "urgency": e.urgency,
                        "status": e.status,
                    }
                    for e in emails
                ],
            }
        )

    return result
