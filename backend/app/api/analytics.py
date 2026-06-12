from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.email_model import Email
import numpy as np

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/sentiment-trend")
def get_sentiment_trend(sender: str = "all", days: int = 30, db: Session = Depends(get_db)):
    # Handle "all" sender to get all emails with sentiment scores
    if sender == "all":
        emails = (
            db.query(Email)
            .filter(Email.sentiment_score.isnot(None))
            .order_by(Email.timestamp.asc())
            .all()
        )
    else:
        emails = (
            db.query(Email)
            .filter(Email.sender == sender, Email.sentiment_score.isnot(None))
            .order_by(Email.timestamp.asc())
            .all()
        )
    
    # Generate moving average tracking
    scores = [e.sentiment_score for e in emails]
    timeline = [{"timestamp": e.timestamp, "score": e.sentiment_score} for e in emails]
    
    # Enforce Layer 3: Deterioration alert check (3 consecutive negative emails)
    consecutive_negative = 0
    alert_triggered = False
    for s in scores:
        if s < -0.3:  # Threshold for negative sentiment
            consecutive_negative += 1
        else:
            consecutive_negative = 0
        if consecutive_negative >= 3:
            alert_triggered = True

    return {
        "sender": sender,
        "timeline": timeline,
        "moving_average": float(np.mean(scores)) if scores else 0.0,
        "sentiment_deterioration_alert": alert_triggered
    }

@router.get("/category-breakdown")
def get_category_breakdown(db: Session = Depends(get_db)):
    results = (
        db.query(Email.category, func.count(Email.id))
        .filter(Email.category.isnot(None))
        .group_by(Email.category)
        .all()
    )
    return {category: count for category, count in results}

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Group by status
    status_counts = db.query(Email.status, func.count(Email.id)).group_by(Email.status).all()
    status_dict = {status: count for status, count in status_counts}

    # Specific urgency and category counts
    critical_count = db.query(Email).filter(Email.urgency == "Critical").count()
    spam_count = db.query(Email).filter(Email.category == "Spam").count()

    return {
        "pending": status_dict.get("Received", 0) + status_dict.get("Processing", 0),
        "replied": status_dict.get("Replied", 0),
        "escalated": status_dict.get("Escalated", 0),
        "critical": critical_count,
        "spam_filtered": spam_count
    }


@router.get("/at-risk-accounts")
def get_at_risk_accounts(db: Session = Depends(get_db)):
    """Find senders with 3+ consecutive negative sentiment emails."""
    # Get all senders with their sentiment scores
    emails = (
        db.query(Email.sender, Email.timestamp, Email.sentiment_score)
        .filter(Email.sentiment_score.isnot(None))
        .order_by(Email.sender, Email.timestamp.asc())
        .all()
    )
    
    # Group by sender and find consecutive negatives
    sender_emails = {}
    for email in emails:
        if email.sender not in sender_emails:
            sender_emails[email.sender] = []
        sender_emails[email.sender].append({
            "timestamp": email.timestamp,
            "score": email.sentiment_score
        })
    
    at_risk = []
    for sender, email_list in sender_emails.items():
        consecutive_negative = 0
        for email in email_list:
            if email["score"] < -0.3:
                consecutive_negative += 1
            else:
                consecutive_negative = 0
            
            if consecutive_negative >= 3:
                at_risk.append({
                    "sender": sender,
                    "timestamp": email["timestamp"],
                    "score": email["score"]
                })
                break  # Only report once per sender
    
    return at_risk