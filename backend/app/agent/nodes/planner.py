# app/agent/nodes/planner.py

from app.agent.state import AgentState
from app.services.planner_service import create_plan


def planner_node(
    state: AgentState
):

    plan = create_plan(
        email_text=state["email_body"],
        classification=state["classification"],
        rag_context=state["rag_context"]
    )
    if (
        state["classification"]["category"]
        == "security_incident"
    ):
        plan.tools = [
            tool
            for tool in plan.tools
            if tool != "draft_reply"
        ]

    state["plan"] = plan.tools

    state["priority"] = plan.priority

    state["reasoning_trace"].append(
        {
            "thought":
                "Need to determine appropriate actions",

            "action":
                "create_plan",

            "observation":
                {
                    "reasoning": plan.reasoning,
                    "tools": plan.tools,
                    "priority": plan.priority
                },

            "next":
                "Execute planned tools"
        }
    )

    return state