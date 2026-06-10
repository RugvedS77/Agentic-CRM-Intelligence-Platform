def flag_for_security(
    email_id: str,
    issue_type: str
):

    return {
        "action": "flag_for_security",
        "email_id": email_id,
        "issue_type": issue_type,
        "assigned_team": "Security Team",
        "status": "queued"
    }