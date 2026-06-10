from sqlalchemy.orm import Session

from app.models.email_model import Email
from app.models.thread_model import Thread


def ingest_email(
    db: Session,
    payload
):

    duplicate = (
        db.query(Email)
        .filter(
            Email.message_id == payload.message_id
        )
        .first()
    )

    if duplicate:
        return {
            "status": "duplicate"
        }

    thread = (
        db.query(Thread)
        .filter(
            Thread.thread_id == payload.thread_id
        )
        .first()
    )

    if not thread:

        thread = Thread(
            thread_id=payload.thread_id,
            subject=payload.subject,
            sender_email=payload.sender,
            first_seen_at=payload.timestamp,
            last_updated_at=payload.timestamp
        )

        db.add(thread)
        db.flush()

    email = Email(
        message_id=payload.message_id,
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        timestamp=payload.timestamp,
        thread_id=thread.id
    )

    db.add(email)

    thread.last_updated_at = payload.timestamp

    db.commit()

    return {
        "status": "success"
    }