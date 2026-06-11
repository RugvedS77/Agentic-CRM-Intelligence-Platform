from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent_run_model import AgentRun


def save_agent_run(
    db: Session,
    email_id: str,
    status: str,
    final_action: str,
    reasoning_trace: list
):

    run = AgentRun(
        email_id=email_id,
        status=status,
        final_action=final_action,
        created_at=datetime.utcnow(),
        reasoning_trace=reasoning_trace
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run