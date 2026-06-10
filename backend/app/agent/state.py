from typing import TypedDict

class AgentState(TypedDict):

    email_id: str

    sender_email: str

    email_body: str

    thread_context: str

    classification: dict

    rag_context: list

    reasoning_trace: list

    tool_calls: int

    dry_run: bool

    plan: list

    final_action: str | None