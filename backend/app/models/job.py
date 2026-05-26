from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Job(BaseModel):
    job_id: str
    title: str
    company: str
    company_logo: Optional[str] = None
    industry: Optional[str] = None
    description: str
    required_skills: List[str]
    preferred_skills: List[str] = []
    experience_level: str
    min_years_experience: int
    max_years_experience: int
    education: Optional[str] = None
    location: str
    remote_type: str
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    employment_type: str
    posted_date: datetime
    application_deadline: Optional[datetime] = None
    url: str
    source: str
    
class JobMatch(BaseModel):
    job: Job
    match_score: float
    skill_match_score: float
    experience_match_score: float
    location_match_score: float
    salary_match_score: float
    match_reasons: str
    skills_you_have: List[str]
    skills_missing: List[str]
