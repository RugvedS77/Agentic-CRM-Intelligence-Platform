# app/agent/nodes/planner.py

from app.agent.state import AgentState
from app.services.planner import create_plan


def planner_node(
    state: AgentState
):

    plan = create_plan(
        email_text=state["email_body"],
        classification=state["classification"],
        rag_context=state["rag_context"]
    )

    state["plan"] = plan.tools

    state["reasoning_trace"].append(
        {
            "thought":
                "Need to determine appropriate actions",

            "action":
                "create_plan",

            "observation":
                {
                    "reasoning": plan.reasoning,
                    "tools": plan.tools
                },

            "next":
                "Execute planned tools"
        }
    )

    return state