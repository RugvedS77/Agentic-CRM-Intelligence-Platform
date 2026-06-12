from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.email_model import Email
from app.services.classifier_service import classify_email
from app.services.planner_service import create_plan
from app.agent.tool_executor import execute_tool

router = APIRouter(tags=["Agent"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/agent/dry-run/{email_id}")
def dry_run_agent(email_id: str, db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.message_id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    email_text = f"{email.subject}\n\n{email.body}"

    classification = classify_email(
        email_content=email_text,
        thread_context="",
        rag_context=""
    )

    plan = create_plan(
        email_text=email_text,
        classification=classification.dict(),
        rag_context=[]
    )

    state = {
        "email_id": email.message_id,
        "sender_email": email.sender,
        "email_body": email.body,
        "thread_context": "",
        "classification": classification.dict(),
        "rag_context": "",
        "reasoning_trace": [],
        "tool_calls": 0,
        "dry_run": True,
        "plan": plan.dict().get("steps", []),
        "tool_results": [],
        "priority": "medium",
        "final_action": None,
    }

    tool_results = []
    for step in plan.dict().get("steps", []):
        result = execute_tool(step["action"], state=state)
        tool_results.append(
            {
                "action": step["action"],
                "status": result.get("status", "unknown") if isinstance(result, dict) else "ok",
                "result": result,
            }
        )

    return {
        "email_id": email.message_id,
        "classification": classification.dict(),
        "plan": plan.dict(),
        "tool_results": tool_results,
    }
