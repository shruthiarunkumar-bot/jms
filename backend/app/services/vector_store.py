import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from typing import List, Dict
import pandas as pd

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.jobs_data = []
        self.dimension = 384
        
        self.embeddings_dir = "data/embeddings"
        os.makedirs(self.embeddings_dir, exist_ok=True)
    
    async def initialize(self):
        if self.load_index():
            print("✓ Loaded existing vector index")
        else:
            print("Creating new vector index...")
            await self.build_index()
    
    async def build_index(self):
        jobs_file = "data/processed/jobs_dataset.csv"
        
        if not os.path.exists(jobs_file):
            print("⚠️ No jobs dataset found. Please scrape jobs first.")
            self.index = faiss.IndexFlatIP(self.dimension)
            return
        
        df = pd.read_csv(jobs_file)
        self.jobs_data = df.to_dict('records')
        
        job_texts = []
        for job in self.jobs_data:
            text = self.create_job_text(job)
            job_texts.append(text)
        
        print(f"Generating embeddings for {len(job_texts)} jobs...")
        embeddings = self.model.encode(job_texts, show_progress_bar=True)
        
        faiss.normalize_L2(embeddings)
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        self.save_index(embeddings)
        
        print(f"✓ Built vector index with {len(job_texts)} jobs")
    
    def create_job_text(self, job: Dict) -> str:
        text = f"""
        Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Description: {job.get('description', '')}
        Required Skills: {', '.join(eval(job.get('required_skills', '[]')) if isinstance(job.get('required_skills'), str) else job.get('required_skills', []))}
        Experience Level: {job.get('experience_level', '')}
        Location: {job.get('location', '')}
        Remote: {job.get('remote_type', '')}
        """
        
        return text.strip()
    
    def create_resume_text(self, resume: Dict) -> str:
        skills = resume.get('skills', [])
        if isinstance(skills, str):
            skills = eval(skills)
        
        text = f"""
        Title: {resume.get('current_title', '')}
        Skills: {', '.join(skills)}
        Experience: {resume.get('total_experience_years', 0)} years
        Summary: {resume.get('summary', '')}
        Education: {resume.get('education_level', '')} in {resume.get('education_field', '')}
        """
        
        return text.strip()
    
    async def search(self, resume_data: Dict, top_k: int = 50) -> List[Dict]:
        if self.index is None or self.index.ntotal == 0:
            return []
        
        resume_text = self.create_resume_text(resume_data)
        resume_embedding = self.model.encode([resume_text])
        
        faiss.normalize_L2(resume_embedding)
        
        distances, indices = self.index.search(
            resume_embedding.astype('float32'),
            min(top_k, self.index.ntotal)
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.jobs_data):
                job = self.jobs_data[idx].copy()
                job['vector_similarity'] = float(distance)
                results.append(job)
        
        return results
    
    def save_index(self, embeddings: np.ndarray):
        faiss.write_index(self.index, f"{self.embeddings_dir}/jobs.index")
        np.save(f"{self.embeddings_dir}/embeddings.npy", embeddings)
        
        with open(f"{self.embeddings_dir}/jobs_data.pkl", 'wb') as f:
            pickle.dump(self.jobs_data, f)
    
    def load_index(self) -> bool:
        try:
            self.index = faiss.read_index(f"{self.embeddings_dir}/jobs.index")
            
            with open(f"{self.embeddings_dir}/jobs_data.pkl", 'rb') as f:
                self.jobs_data = pickle.load(f)
            
            return True
        except:
            return False
