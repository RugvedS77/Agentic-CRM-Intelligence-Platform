MAX_TOOL_CALLS = 6

def increment_tool_calls(state):

    state["tool_calls"] += 1

    if state["tool_calls"] > MAX_TOOL_CALLS:

        raise Exception(
            "Maximum tool calls exceeded"
        )

    return state