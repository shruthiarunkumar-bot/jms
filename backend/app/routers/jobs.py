from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs")
async def list_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    remote: Optional[bool] = Query(None),
    limit: int = Query(20, le=50),
):
    """Search jobs directly without a resume."""
    try:
        from app.services.job_fetcher import _fetch_mantiks_jobs, _normalize_job
        
        params = {
            "job_title": query or "Software Engineer",
            "location": location or "",
        }
        if remote is not None:
            params["remote"] = remote
        
        raw_jobs = _fetch_mantiks_jobs(params)
        jobs = [j for raw in raw_jobs if (j := _normalize_job(raw))]
        
        return {
            "success": True,
            "jobs": jobs[:limit],
            "total": len(jobs),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    raise HTTPException(status_code=404, detail="Job detail not cached. Use search.")