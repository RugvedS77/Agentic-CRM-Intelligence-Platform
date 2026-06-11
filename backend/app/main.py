from fastapi import FastAPI

from app.utils.db_health import router as db_health_router
from app.api.ingest import router as ingest_router
from app.api.threads import router as thread_router

from app.api.rag import router as rag_router
from app.api.classifier import router as classifier_router
from app.api.planner import router as planner_router

from app.api.agent import router as agent_router

app = FastAPI(
    title="SenAI CRM Intelligence Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "SenAI CRM Intelligence Platform"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

app.include_router(db_health_router)
app.include_router(ingest_router)
app.include_router(thread_router)
app.include_router(rag_router)
app.include_router(classifier_router)
app.include_router(planner_router)
app.include_router(agent_router)