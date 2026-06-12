from app.agent.state import AgentState


def finish_node(state: AgentState):
    # Terminal node: ensure final_action is set from the last planned tool if available
    if not state.get("final_action") and state.get("plan"):
        state["final_action"] = state["plan"][-1]

    state["reasoning_trace"].append(
        {
            "thought": "Agent execution complete",
            "action": "finish",
            "observation": {
                "final_action": state.get("final_action"),
                "tool_calls": state.get("tool_calls", 0),
            },
            "next": "End of workflow",
        }
    )

    return state
