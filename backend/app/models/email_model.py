from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True)

    message_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    thread_id = Column(
        Integer,
        ForeignKey("threads.id")
    )

    sender = Column(String, nullable=False)

    subject = Column(String)

    body = Column(Text)

    timestamp = Column(DateTime)

    category = Column(String)

    sentiment = Column(String)

    sentiment_score = Column(Float)

    urgency = Column(String)

    confidence = Column(Float)

    requires_human = Column(Boolean)

    raw_entities = Column(JSONB)

    status = Column(
        String,
        default="Received"
    )