from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Status"])

JOB_STORE = {}


@router.get("/api/status/{job_id}")
def get_job_status(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
