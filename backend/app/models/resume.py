from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class ResumeData(BaseModel):
    resume_id: Optional[str] = None
    candidate_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: float
    current_title: Optional[str] = None
    skills: List[str]
    education_level: Optional[str] = None
    education_field: Optional[str] = None
    previous_companies: List[str] = []
    preferred_locations: List[str] = []
    remote_preference: bool = False
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    created_at: datetime = datetime.now()

class ResumeUploadResponse(BaseModel):
    success: bool
    resume_id: str
    message: str
    extracted_data: Optional[ResumeData] = None
