from langgraph.graph import StateGraph # type: ignore

from app.agent.state import AgentState

from app.agent.nodes.classify import classify_node
from app.agent.nodes.planner import planner_node
from app.agent.nodes.execute import execute_node
from app.agent.nodes.finish import finish_node


builder = StateGraph(AgentState)

builder.add_node(
    "classifier",
    classify_node
)

builder.add_node(
    "planner",
    planner_node
)

builder.add_node(
    "execute",
    execute_node
)

builder.add_node(
    "finish",
    finish_node
)

builder.set_entry_point(
    "classifier"
)

builder.add_edge(
    "classifier",
    "planner"
)

builder.add_edge(
    "planner",
    "execute"
)

builder.add_edge(
    "execute",
    "finish"
)

graph = builder.compile()