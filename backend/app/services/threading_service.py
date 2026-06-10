from sqlalchemy.orm import Session

from app.models.thread_model import Thread
from app.models.email_model import Email


def build_thread_context(
    db: Session,
    thread_id: str
):

    thread = (
        db.query(Thread)
        .filter(Thread.thread_id == thread_id)
        .first()
    )

    if not thread:
        return ""

    emails = (
        db.query(Email)
        .filter(Email.thread_id == thread.id)
        .order_by(Email.timestamp.asc())
        .all()
    )

    context = []

    for email in emails:

        context.append(
            f"""
Sender: {email.sender}

Subject: {email.subject}

Message:
{email.body}
"""
        )

    return "\n\n---\n\n".join(context)