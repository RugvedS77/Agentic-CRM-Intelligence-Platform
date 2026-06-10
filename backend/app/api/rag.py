from fastapi import APIRouter

from app.rag.retriever import retrieve_context

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.get("/search")
def rag_search(q: str):

    results = retrieve_context(q)

    return {
        "query": q,
        "top_k": len(results),
        "results": results
    }