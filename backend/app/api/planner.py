from fastapi import APIRouter
from pydantic import BaseModel

from app.services.planner_service import create_plan

router = APIRouter(
    prefix="/planner",
    tags=["Planner"]
)


class PlannerRequest(BaseModel):
    email: str


@router.post("/test")
def test_planner(
    request: PlannerRequest
):

    plan = create_plan(
        email_text=request.email,
        classification={},
        rag_context=[]
    )

    return plan