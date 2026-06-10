from app.core.database import SessionLocal
from app.models.email_model import Email


def get_thread_history(sender_email: str):

    db = SessionLocal()

    emails = (
        db.query(Email)
        .filter(
            Email.sender == sender_email
        )
        .order_by(Email.timestamp.asc())
        .all()
    )

    return [
        {
            "message_id": e.message_id,
            "subject": e.subject,
            "body": e.body,
            "timestamp": str(e.timestamp)
        }
        for e in emails
    ]