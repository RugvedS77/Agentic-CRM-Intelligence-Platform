from sqlalchemy.orm import Session
from datetime import datetime
import re

from app.models.email_model import Email
from app.models.thread_model import Thread
from app.models.contact_model import Contact
from app.services.priority import calculate_priority


SPAM_BLOCKLIST = [
    "boost your seo",
    "front page of google",
    "limited offer",
    "click here to claim",
    "dear sir/madam",
    "dear sir or madam"
]

SECURITY_KEYWORDS = [
    "login attempt",
    "breach",
    "ransomware",
    "data leak",
    "unauthorized access",
    "north korea",
    "p0",
    "production down"
]

LEGAL_KEYWORDS = [
    "cease and desist",
    "legal action",
    "lawsuit",
    "attorney",
    "gdpr",
    "article 20",
    "data portability",
    "right to erasure"
]

INTERNAL_DOMAINS = [
    "internal.com",
    "mycompany.com"
]


def _normalize_text(value: str) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def _classify_prefilter(sender: str, subject: str, body: str):
    text = f"{subject} {body}".lower()
    sender_lower = sender.lower()

    for domain in INTERNAL_DOMAINS:
        if sender_lower.endswith(f"@{domain}"):
            return {
                "route": "internal",
                "reason": f"Internal domain detected: {domain}"
            }

    for keyword in SECURITY_KEYWORDS:
        if keyword in text:
            return {
                "route": "security",
                "reason": f"Security keyword detected: {keyword}"
            }

    for keyword in LEGAL_KEYWORDS:
        if keyword in text:
            return {
                "route": "legal",
                "reason": f"Legal keyword detected: {keyword}"
            }

    for phrase in SPAM_BLOCKLIST:
        if phrase in text:
            return {
                "route": "spam",
                "reason": f"Spam pattern detected: {phrase}"
            }

    return {
        "route": "standard",
        "reason": None
    }


def ingest_email(
    db: Session,
    payload
):
    subject = _normalize_text(payload.subject)
    body = _normalize_text(payload.body)

    if not subject:
        return {
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Subject is required."
        }

    if not body:
        return {
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Body is required."
        }

    if len(body) > 10000:
        body = body[:10000]

    prefilter = _classify_prefilter(payload.sender, subject, body)

    duplicate = (
        db.query(Email)
        .filter(
            Email.message_id == payload.message_id
        )
        .first()
    )

    if duplicate:
        return {
            "status": "duplicate",
            "prefilter": prefilter
        }

    thread = (
        db.query(Thread)
        .filter(
            Thread.thread_id == payload.thread_id
        )
        .first()
    )

    if not thread:
        thread = Thread(
            thread_id=payload.thread_id,
            subject=subject,
            sender_email=payload.sender,
            first_seen_at=payload.timestamp,
            last_updated_at=payload.timestamp
        )

        db.add(thread)
        db.flush()
    else:
        if payload.timestamp < thread.first_seen_at:
            thread.first_seen_at = payload.timestamp
        if payload.timestamp > thread.last_updated_at:
            thread.last_updated_at = payload.timestamp

    priority = calculate_priority(subject, body)

    email = Email(
        message_id=payload.message_id,
        sender=payload.sender,
        subject=subject,
        body=body,
        timestamp=payload.timestamp,
        thread_id=thread.id
    )

    db.add(email)

    # Auto-create contact for sender if not exists
    existing_contact = db.query(Contact).filter(
        Contact.email == payload.sender
    ).first()
    
    if not existing_contact:
        # Extract company from email domain
        domain = payload.sender.split("@")[-1].split(".")[0] if "@" in payload.sender else "Unknown"
        contact = Contact(
            email=payload.sender,
            name=payload.sender.split("@")[0].replace(".", " ").title(),
            company=domain.title(),
            status="Active",
            account_value=0,
            churn_risk_score=0.0,
            subscription_tier="Standard",
            billing_status="Active",
            overdue_invoices=0,
            vip_status=False
        )
        db.add(contact)

    db.commit()

    return {
        "status": "success",
        "priority": priority,
        "prefilter": prefilter
    }