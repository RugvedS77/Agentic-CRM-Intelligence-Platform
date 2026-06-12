from app.agent.tool_executor import (
    execute_tool
)

from app.agent.utils import (
    increment_tool_calls
)


def execute_node(state):

    if state.get("dry_run"):

        state["reasoning_trace"].append(
            {
                "thought": "Dry run enabled",
                "action": "skip_execution",
                "observation": state["plan"],
                "next": "Return plan"
            }
        )

        state["tool_results"] = []

        return state

    observations = []

    for tool_name in state["plan"]:
        try:
            increment_tool_calls(state)
        except Exception as e:
            observations.append({
                "tool": "system_limit",
                "result": {"error": str(e)}
            })
            observations.append({
                "tool": "escalate_to_human",
                "result": {"status": "forced_escalation", "reason": "Max tool calls exceeded"}
            })
            break

        try:
            result = execute_tool(tool_name, state)
            observations.append({"tool": tool_name, "result": result})
        except Exception as e:
            observations.append({"tool": tool_name, "result": {"error": str(e)}})

    state["tool_results"] = observations

    state["reasoning_trace"].append(
        {
            "thought":
                "Execute planned tools",

            "action":
                state["plan"],

            "observation":
                observations,

            "next":
                "Generate final outcome"
        }
    )

    return state