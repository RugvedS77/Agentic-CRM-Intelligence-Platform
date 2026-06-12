from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class WebIntelligenceCache(Base):
    __tablename__ = "web_intelligence_cache"

    id = Column(Integer, primary_key=True)
    source_url = Column(String, index=True)
    target_entity = Column(String, index=True)
    scraped_data = Column(JSONB)
    scraped_at = Column(DateTime)
    expires_at = Column(DateTime)