from app.rag.retriever import retrieve_context

from app.tools.contact_tools import (
    get_contact_profile,
    check_account_status
)

from app.tools.thread_tools import (
    get_thread_history
)

from app.tools.legal_tools import (
    flag_for_legal
)

from app.tools.security_tools import (
    flag_for_security
)

from app.tools.escalation_tools import (
    escalate_to_human
)

from app.tools.reply_tools import (
    draft_reply
)


def execute_tool(
    tool_name: str,
    state: dict
):

    email = state["sender_email"]
    email_id = state["email_id"]

    if tool_name == "search_knowledge_base":

        return retrieve_context(
            state["email_body"],
            k=3
        )

    elif tool_name == "get_thread_history":

        return get_thread_history(email)

    elif tool_name == "get_contact_profile":

        return get_contact_profile(email)

    elif tool_name == "check_account_status":

        return check_account_status(email)

    elif tool_name == "flag_for_legal":

        return flag_for_legal(
            email_id=email_id,
            issue_type=state["classification"]["category"]
        )

    elif tool_name == "flag_for_security":

        return flag_for_security(
            email_id=email_id,
            issue_type=state["classification"]["category"]
        )

    elif tool_name == "escalate_to_human":

        return escalate_to_human(
            email_id=email_id,
            reason=state["classification"]["category"],
            priority=state.get(
                "priority",
                "high"
            )
        )

    elif tool_name == "draft_reply":

        return draft_reply(
            email_body=state["email_body"],
            rag_context=state["rag_context"]
        )

    return {
        "error": f"Unknown tool {tool_name}"
    }