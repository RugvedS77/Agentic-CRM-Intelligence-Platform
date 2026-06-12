from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.web_intell_model import WebIntelligenceCache
from app.tools.intel_tools import scrape_public_sentiment

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

@router.get("/reputation")
def get_reputation(company_name: str = "SenAI", db: Session = Depends(get_db)):
    now = datetime.utcnow()
    
    cached = db.query(WebIntelligenceCache).filter(
        WebIntelligenceCache.target_entity == company_name,
        WebIntelligenceCache.expires_at > now
    ).order_by(WebIntelligenceCache.scraped_at.desc()).first()
    
    if cached:
        return cached.scraped_data
    
    # Trigger live scrape if no cache
    scraped_data = scrape_public_sentiment(company_name)
    
    if scraped_data.get("source") == "fallback":
        return {
            "status": "Live scraping failed. Check network connectivity or robots.txt compliance.",
            "data": scraped_data.get("data", {})
        }
    
    return scraped_data.get("data", scraped_data)