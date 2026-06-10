from app.core.database import SessionLocal
from app.models.contact_model import Contact


db = SessionLocal()

contacts = [

    Contact(
        email="bob.jones@enterprise.net",
        name="Bob Jones",
        company="Enterprise Corp",
        account_value=250000,
        churn_risk_score=0.85,
        vip_status=True,
        subscription_tier="Enterprise",
        billing_status="Renewal On Hold",
        overdue_invoices=1
    ),

    Contact(
        email="karen.w@retail-co.com",
        name="Karen Williams",
        company="Retail Co",
        account_value=30000,
        churn_risk_score=0.92,
        vip_status=False,
        subscription_tier="Professional",
        billing_status="Active",
        overdue_invoices=0
    ),

    Contact(
        email="alice.smith@greenlight-npo.org",
        name="Alice Smith",
        company="Greenlight NPO",
        account_value=10000,
        churn_risk_score=0.20,
        vip_status=False,
        subscription_tier="Standard",
        billing_status="Active",
        overdue_invoices=0
    )
]


for contact in contacts:
    existing = db.query(Contact).filter(
        Contact.email == contact.email
    ).first()

    if not existing:
        db.add(contact)

db.commit()

print("Contacts seeded")