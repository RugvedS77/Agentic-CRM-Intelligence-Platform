from app.agent.state import AgentState
from app.services.classifier_service import classify_email
from app.rag.retriever import retrieve_context


def classify_node(
    state: AgentState
):
    rag_chunks = retrieve_context(
        state["email_body"],
        k=3
    )

    rag_context = "\n\n".join(
        [
            f"Source: {chunk['source']}\n{chunk['content']}"
            for chunk in rag_chunks
        ]
    )
    state["rag_context"] = rag_context
    
    result = classify_email(
        email_content=state["email_body"],
        thread_context=state["thread_context"],
        rag_context=rag_context
    )

    state["classification"] = (
        result.model_dump()
    )

    state["reasoning_trace"].append(
        {
            "thought": "Need to understand customer intent",
            "action": "classify_email",
            "observation": result.model_dump(),
            "next": "Determine best action"
        }
    )

    return state