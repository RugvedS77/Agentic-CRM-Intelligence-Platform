def flag_for_legal(
    email_id: str,
    issue_type: str
):

    return {
        "action": "flag_for_legal",
        "email_id": email_id,
        "issue_type": issue_type,
        "assigned_team": "Legal Team",
        "status": "queued"
    }