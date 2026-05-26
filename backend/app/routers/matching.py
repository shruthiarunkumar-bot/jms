from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api", tags=["matching"])


class MatchRequest(BaseModel):
    resume_text: str
    top_k: Optional[int] = 10
    location: Optional[str] = None
    job_type: Optional[str] = None


@router.post("/match")
async def match_jobs(request: MatchRequest):
    """Match jobs from raw resume text."""
    if not request.resume_text or len(request.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text too short.")
    
    try:
        from app.services.ai_matcher import (
            parse_resume_with_claude,
            embed_resume,
            semantic_match_jobs,
            compute_granular_score,
            generate_match_explanation,
        )
        from app.services.job_fetcher import fetch_jobs_for_resume
        
        parsed = parse_resume_with_claude(request.resume_text)
        resume_vector = embed_resume(parsed)
        jobs = fetch_jobs_for_resume(parsed)
        
        if not jobs:
            raise HTTPException(status_code=404, detail="No jobs found. Try again later.")
        
        matched = semantic_match_jobs(resume_vector, jobs, top_k=request.top_k * 2)
        
        results = []
        for job in matched[:request.top_k]:
            scores = compute_granular_score(parsed, job, job.get('semantic_score', 0.5))
            explanation = generate_match_explanation(parsed, job, scores)
            results.append({**job, **scores, "explanation": explanation})
        
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            "success": True,
            "resume": parsed,
            "matches": results,
            "total_jobs_searched": len(jobs),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matches/{resume_id}")
async def get_matches(resume_id: str):
    """Placeholder for cached match retrieval."""
    raise HTTPException(status_code=404, detail="Use POST /api/upload to get matches.")