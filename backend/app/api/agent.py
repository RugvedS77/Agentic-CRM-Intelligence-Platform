from fastapi import APIRouter
from pydantic import BaseModel

from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

from app.rag.retriever import retrieve_context
from app.services.classifier_service import classify_email
from app.services.planner_service import create_plan

from app.agent.nodes.execute import execute_node

from app.services.agent_run_service import save_agent_run
from app.agent.graph import graph

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


class AgentTestRequest(BaseModel):
    email: str
    thread_context: str = ""

class AgentRunRequest(BaseModel):
    email_id: str
    sender_email: str
    email_body: str
    thread_context: str = ""
    dry_run: bool = False

@router.post("/test")
def test_agent(
    request: AgentTestRequest,
    db: Session = Depends(get_db)
):

    rag_chunks = retrieve_context(
        request.email,
        k=3
    )

    rag_context = "\n\n".join(
        [
            f"Source: {chunk['source']}\n"
            f"{chunk['content']}"
            for chunk in rag_chunks
        ]
    )

    classification = classify_email(
        email_content=request.email,
        thread_context=request.thread_context,
        rag_context=rag_context
    )

    plan = create_plan(
        email_text=request.email,
        classification=classification.model_dump(),
        rag_context=rag_chunks
    )

    state = {
        "email_id": "test_email",
        "sender_email": "bob.jones@enterprise.net",
        "email_body": request.email,
        "thread_context": request.thread_context,
        "classification": classification.model_dump(),
        "rag_context": rag_chunks,
        "reasoning_trace": [],
        "tool_calls": 0,
        "dry_run": True,
        "plan": plan.tools,
        "priority": plan.priority
    }

    state = execute_node(state)

    save_agent_run(
        db=db,
        email_id=state["email_id"],
        status="completed",
        final_action=state["plan"][-1]
            if state["plan"]
            else "none",
        reasoning_trace=state["reasoning_trace"]
    )

    return {
        "classification": classification.model_dump(),
        "plan": plan.model_dump(),
        "tool_results": state["tool_results"]
    }

@router.post("/run")
def run_agent(
    request: AgentRunRequest,
    db: Session = Depends(get_db)
):

    state = {
        "email_id": request.email_id,
        "sender_email": request.sender_email,
        "email_body": request.email_body,
        "thread_context": request.thread_context,

        "classification": None,
        "rag_context": [],

        "plan": [],
        "priority": "normal",

        "tool_results": [],

        "tool_calls": 0,
        "reasoning_trace": [],

        "dry_run": request.dry_run
    }

    result = graph.invoke(state)

    save_agent_run(
        db=db,
        email_id=result["email_id"],
        status="completed",
        final_action=(
            result["plan"][-1]
            if result["plan"]
            else "none"
        ),
        reasoning_trace=result["reasoning_trace"]
    )

    return {
        "classification":
            result["classification"],

        "plan":
            result["plan"],

        "tool_results":
            result["tool_results"],

        "reasoning_trace":
            result["reasoning_trace"]
    }