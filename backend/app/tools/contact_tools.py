from app.core.database import SessionLocal
from app.models.contact_model import Contact


def get_contact_profile(email: str):

    db = SessionLocal()

    contact = (
        db.query(Contact)
        .filter(Contact.email == email)
        .first()
    )

    if not contact:
        return {
            "found": False
        }

    return {
        "found": True,
        "email": contact.email,
        "name": contact.name,
        "company": contact.company,
        "account_value": contact.account_value,
        "churn_risk_score": contact.churn_risk_score,
        "vip_status": contact.vip_status
    }

def check_account_status(email: str):

    db = SessionLocal()

    contact = (
        db.query(Contact)
        .filter(Contact.email == email)
        .first()
    )

    if not contact:
        return {
            "found": False
        }

    return {
        "found": True,
        "subscription_tier": contact.subscription_tier,
        "billing_status": contact.billing_status,
        "overdue_invoices": contact.overdue_invoices
    }