from typing import TypedDict

class AgentState(TypedDict):

    email_id: str

    sender_email: str

    email_body: str

    thread_context: str

    classification: dict

    rag_context: str

    reasoning_trace: list

    tool_calls: int

    dry_run: bool

    plan: list

    tool_results: list
    priority: str

    final_action: str | None