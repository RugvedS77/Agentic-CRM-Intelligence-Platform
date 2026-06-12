from fastapi import FastAPI

from app.utils.db_health import router as db_health_router
from app.api.ingest import router as ingest_router
from app.api.threads import router as thread_router
from app.api.stream import router as stream_router

from app.api.rag import router as rag_router
from app.api.classifier import router as classifier_router
from app.api.planner import router as planner_router

from app.api.agent import router as agent_router
from app.api.intel import router as intel_router
from app.api.analytics import router as analytics_router
from app.api.contacts import router as contacts_router
from app.api.audit import router as audit_router
from app.api.actions import router as actions_router
from app.api.inbox import router as inbox_router
from app.api.status import router as status_router
from app.api.threads_lookup import router as threads_lookup_router
from app.api.dry_run import router as dry_run_router
from app.api.benchmarks import router as benchmarks_router

app = FastAPI(
    title="SenAI CRM Intelligence Platform",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Override default validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "The request payload is invalid.",
            "details": exc.errors()
        }
    )

# Override standard HTTP exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": "HTTP_ERROR",
            "message": exc.detail,
            "details": str(exc.detail)
        }
    )

# Catch-all for unhandled server errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "details": str(exc)
        }
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
app.include_router(stream_router)
app.include_router(rag_router)
app.include_router(classifier_router)
app.include_router(planner_router)
app.include_router(agent_router)
app.include_router(intel_router)
app.include_router(analytics_router)
app.include_router(contacts_router)
app.include_router(audit_router)
app.include_router(actions_router)
app.include_router(inbox_router)
app.include_router(status_router)
app.include_router(threads_lookup_router)
app.include_router(dry_run_router)
app.include_router(benchmarks_router)
