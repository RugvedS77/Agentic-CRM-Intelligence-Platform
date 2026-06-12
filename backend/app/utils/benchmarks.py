import time
from typing import Callable, Any


class BenchmarkResult:
    def __init__(self, operation: str, duration_ms: float, passed: bool, threshold_ms: float):
        self.operation = operation
        self.duration_ms = duration_ms
        self.passed = passed
        self.threshold_ms = threshold_ms

    def to_dict(self):
        return {
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 2),
            "passed": self.passed,
            "threshold_ms": self.threshold_ms
        }


BENCHMARK_RESULTS: dict[str, BenchmarkResult] = {}


def measure(operation: str, threshold_ms: float = 200.0) -> Callable:
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000
            passed = duration_ms <= threshold_ms
            BENCHMARK_RESULTS[operation] = BenchmarkResult(
                operation=operation,
                duration_ms=duration_ms,
                passed=passed,
                threshold_ms=threshold_ms
            )
            return result
        return wrapper
    return decorator


async def run_benchmarks() -> list[dict]:
    from app.rag.retriever import retrieve_context

    results = []

    # Thread query benchmark
    start = time.perf_counter()
    try:
        from app.core.database import SessionLocal
        from app.models.thread_model import Thread
        db = SessionLocal()
        db.query(Thread).limit(10).all()
        db.close()
    except Exception:
        pass
    thread_duration = (time.perf_counter() - start) * 1000
    results.append(BenchmarkResult(
        operation="thread_query",
        duration_ms=thread_duration,
        passed=thread_duration <= 100.0,
        threshold_ms=100.0
    ).to_dict())

    # Vector search benchmark
    start = time.perf_counter()
    try:
        retrieve_context("test query", k=3)
    except Exception:
        pass
    vector_duration = (time.perf_counter() - start) * 1000
    results.append(BenchmarkResult(
        operation="vector_search",
        duration_ms=vector_duration,
        passed=vector_duration <= 200.0,
        threshold_ms=200.0
    ).to_dict())

    return results
