from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from datetime import datetime

class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True)
    email_id = Column(String, index=True)
    agent_reasoning_log = Column(JSONB)  # Store summary of Thought->Action->Observation
    action_type = Column(String)  # Auto-Reply | Escalate | Legal-Flag | Ticket-Created | Ignored
    proposed_content = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)