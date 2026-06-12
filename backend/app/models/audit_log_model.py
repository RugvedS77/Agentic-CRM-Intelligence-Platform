from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String, index=True)  # e.g., "contact", "draft"
    entity_id = Column(String, index=True)
    action = Column(String)  # e.g., "STATUS_UPDATE", "DRAFT_APPROVED"
    performed_by = Column(String)  # agent or user_id
    timestamp = Column(DateTime, default=datetime.utcnow)
    diff = Column(JSONB)  # changes description