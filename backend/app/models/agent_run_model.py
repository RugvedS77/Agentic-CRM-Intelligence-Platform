from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True)

    email_id = Column(String)

    status = Column(String)

    final_action = Column(String)

    created_at = Column(DateTime)

    reasoning_trace = Column(JSONB)