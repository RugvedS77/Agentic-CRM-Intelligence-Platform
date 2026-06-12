from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent_run_model import AgentRun
from app.models.audit_log_model import AuditLog


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
    
    # Create audit log entry for agent run
    audit = AuditLog(
        entity_type="agent_run",
        entity_id=str(run.id),
        action="AGENT_EXECUTED",
        performed_by="system",
        diff={
            "email_id": email_id,
            "status": status,
            "final_action": final_action
        }
    )
    db.add(audit)
    
    db.commit()
    db.refresh(run)

    return run

def get_agent_runs(db):
    return (
        db.query(AgentRun)
        .order_by(
            AgentRun.created_at.desc()
        )
        .all()
    )