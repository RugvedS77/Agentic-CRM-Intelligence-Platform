from fastapi import APIRouter

from app.services.classifier_service import classify_email

router = APIRouter(
    prefix="/classifier",
    tags=["Classifier"]
)


@router.get("/test")
def test_classifier(q: str):

    result = classify_email(
        email_content=q,
        thread_context=""
    )

    return result