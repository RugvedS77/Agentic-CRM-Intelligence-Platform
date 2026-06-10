from app.agent.state import AgentState
from app.services.classifier_service import classify_email


def classify_node(
    state: AgentState
):

    result = classify_email(
        email_content=state["email_body"],
        thread_context=state["thread_context"]
    )

    state["classification"] = (
        result.model_dump()
    )

    state["reasoning_trace"].append(
        {
            "thought":
                "Need to understand customer intent",

            "action":
                "classify_email",

            "observation":
                result.model_dump(),

            "next":
                "Determine best action"
        }
    )

    return state