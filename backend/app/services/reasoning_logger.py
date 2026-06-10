from datetime import datetime

from app.core.database import SessionLocal
from app.models.agent_run_model import AgentRun


def save_agent_run(
    email_id: str,
    final_action: str,
    reasoning_trace: list,
    status: str = "completed"
):

    db = SessionLocal()

    run = AgentRun(
        email_id=email_id,
        status=status,
        final_action=final_action,
        created_at=datetime.utcnow(),
        reasoning_trace=reasoning_trace
    )

    db.add(run)
    db.commit()

    return run.id