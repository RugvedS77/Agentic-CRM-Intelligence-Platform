from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime, Boolean
)

from app.core.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)

    email = Column(
        String,
        unique=True,
        index=True
    )

    name = Column(String)

    company = Column(String)

    status = Column(
        String,
        default="Active"
    )

    account_value = Column(Float, default=0)

    churn_risk_score = Column(Float, default=0)

    subscription_tier = Column(
        String,
        default="Standard"
    )

    billing_status = Column(
        String,
        default="Active"
    )

    overdue_invoices = Column(
        Integer,
        default=0
    )

    vip_status = Column(
        Boolean,
        default=False
    )

    created_at = Column(DateTime)

    last_contact_at = Column(DateTime)