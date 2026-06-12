from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class EmailCategory(str, Enum):
    COMPLAINT = "Complaint"
    INQUIRY = "Inquiry"
    BUG_REPORT = "Bug Report"
    FEATURE_REQUEST = "Feature Request"
    COMPLIANCE = "Compliance"
    LEGAL = "Legal"
    BILLING = "Billing"
    SPAM = "Spam"
    INTERNAL = "Internal"
    SECURITY = "Security"
    OTHER = "Other"

class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"
    MIXED = "Mixed"

class UrgencyEnum(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class DetectedEntities(BaseModel):
    order_ids: List[str] = []
    ticket_ids: List[str] = []
    monetary_amounts: List[str] = []
    deadlines: List[str] = []
    products_mentioned: List[str] = []

class ClassificationResult(BaseModel):
    category: EmailCategory
    sentiment: SentimentEnum
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    urgency: UrgencyEnum
    requires_human: bool
    escalation_reason: Optional[str] = None
    suggested_reply: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    detected_entities: DetectedEntities
    reasoning: str