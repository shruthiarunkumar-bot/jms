import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class SimpleDB:
    """Simple JSON-based database"""
    
    def __init__(self, db_file: str = "data/user_data.json"):
        self.db_file = db_file
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.data = self.load()
    
    def load(self) -> Dict:
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {
            "resumes": {},
            "saved_jobs": {},
            "applications": {}
        }
    
    def save(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def save_resume(self, resume_id: str, resume_data: Dict) -> str:
        self.data["resumes"][resume_id] = {
            **resume_data,
            "created_at": datetime.now().isoformat()
        }
        self.save()
        return resume_id
    
    def get_resume(self, resume_id: str) -> Optional[Dict]:
        return self.data["resumes"].get(resume_id)
    
    def save_job(self, resume_id: str, job_id: str) -> bool:
        key = f"{resume_id}_{job_id}"
        if key not in self.data["saved_jobs"]:
            self.data["saved_jobs"][key] = {
                "resume_id": resume_id,
                "job_id": job_id,
                "saved_at": datetime.now().isoformat()
            }
            self.save()
            return True
        return False
    
    def get_saved_jobs(self, resume_id: str) -> List[str]:
        return [
            v["job_id"] 
            for k, v in self.data["saved_jobs"].items() 
            if v["resume_id"] == resume_id
        ]

db = SimpleDB()
