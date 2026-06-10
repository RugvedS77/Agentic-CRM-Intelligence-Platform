from app.rag.vector_store import vectorstore


def retrieve_context(
    query: str,
    k: int = 3
):
    results = vectorstore.similarity_search_with_relevance_scores(
        query=query,
        k=k
    )

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source"),
            "relevance_score": round(score, 4)
        }
        for doc, score in results
    ]