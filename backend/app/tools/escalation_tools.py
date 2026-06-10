def escalate_to_human(
    email_id: str,
    reason: str,
    priority: str
):

    return {
        "action": "escalate_to_human",
        "email_id": email_id,
        "reason": reason,
        "priority": priority,
        "status": "queued"
    }