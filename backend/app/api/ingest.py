from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.schemas.email_schema import EmailPayload

from app.core.database import get_db

from app.services.ingestion_service import (
    ingest_email
)

router = APIRouter()


@router.post("/api/ingest")
def ingest(
    payload: EmailPayload,
    db: Session = Depends(get_db)
):

    return ingest_email(
        db,
        payload
    )