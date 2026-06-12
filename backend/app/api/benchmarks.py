from fastapi import APIRouter
from app.utils.benchmarks import run_benchmarks

router = APIRouter(tags=["Benchmarks"])


@router.get("/benchmarks")
async def get_benchmarks():
    results = await run_benchmarks()
    return {
        "benchmarks": results,
        "all_passed": all(item["passed"] for item in results)
    }
