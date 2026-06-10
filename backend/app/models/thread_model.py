from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text
)

from app.core.database import Base


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True)

    thread_id = Column(
        String,
        unique=True,
        index=True
    )

    subject = Column(String)

    sender_email = Column(String)

    first_seen_at = Column(DateTime)

    last_updated_at = Column(DateTime)

    status = Column(
        String,
        default="Open"
    )

    assigned_to = Column(String)

    summary = Column(Text)