from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.thread_model import Thread
from app.models.email_model import Email

from app.services.threading_service import (
    build_thread_context
)

router = APIRouter(prefix="/threads", tags=["Threads"])


@router.get("/{thread_id}")
def get_thread(
    thread_id: str,
    db: Session = Depends(get_db)
):

    thread = (
        db.query(Thread)
        .filter(Thread.thread_id == thread_id)
        .first()
    )

    if not thread:
        raise HTTPException(
            status_code=404,
            detail="Thread not found"
        )

    emails = (
        db.query(Email)
        .filter(Email.thread_id == thread.id)
        .order_by(Email.timestamp.asc())
        .all()
    )

    return {
        "thread": {
            "id": thread.thread_id,
            "subject": thread.subject,
            "summary": thread.summary,
        },
        "emails": [
            {
                "message_id": e.message_id,
                "sender": e.sender,
                "subject": e.subject,
                "body": e.body,
                "timestamp": e.timestamp,
            }
            for e in emails
        ]
    }

@router.get("/{thread_id}/context")
def get_context(
    thread_id: str,
    db: Session = Depends(get_db)
):

    return {
        "context": build_thread_context(
            db,
            thread_id
        )
    }