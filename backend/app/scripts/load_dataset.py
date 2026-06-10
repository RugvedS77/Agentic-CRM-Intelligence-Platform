import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.email_model import Email
from app.models.thread_model import Thread
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent / "email-data-advanced.json"

def load_dataset():

    db: Session = SessionLocal()

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        emails = json.load(f)

    inserted = 0

    for item in emails:

        existing = (
            db.query(Email)
            .filter(
                Email.message_id == item["message_id"]
            )
            .first()
        )

        if existing:
            continue

        thread = (
            db.query(Thread)
            .filter(
                Thread.thread_id == item["thread_id"]
            )
            .first()
        )

        if not thread:

            thread = Thread(
                thread_id=item["thread_id"],
                subject=item["subject"],
                sender_email=item["sender"],
                first_seen_at=datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                ),
                last_updated_at=datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                ),
            )

            db.add(thread)
            db.flush()

        email = Email(
            message_id=item["message_id"],
            sender=item["sender"],
            subject=item["subject"],
            body=item["body"],
            timestamp=datetime.fromisoformat(
                item["timestamp"].replace("Z", "+00:00")
            ),
            thread_id=thread.id,
        )

        db.add(email)

        inserted += 1

    db.commit()

    print(f"Inserted {inserted} emails")


if __name__ == "__main__":
    load_dataset()