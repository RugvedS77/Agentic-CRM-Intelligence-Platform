from enum import Enum

from pydantic import BaseModel


class EmailCategory(str, Enum):
    BILLING = "billing"
    REFUND = "refund"
    TECHNICAL_SUPPORT = "technical_support"
    GDPR_REQUEST = "gdpr_request"
    SECURITY_INCIDENT = "security_incident"
    LEGAL_THREAT = "legal_threat"
    VIP_CHURN = "vip_churn"
    GENERAL_INQUIRY = "general_inquiry"
    SPAM = "spam"


class ClassificationResult(BaseModel):
    category: EmailCategory
    confidence: float
    reasoning: str