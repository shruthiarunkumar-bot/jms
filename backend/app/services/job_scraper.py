import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()


class JobScraper:

    def __init__(self):
        self.jsearch_key = os.getenv("JSEARCH_API_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
        self.base_url = "https://jsearch.p.rapidapi.com/search"

        if not self.jsearch_key:
            raise ValueError("❌ JSEARCH_API_KEY not found in .env")

    async def scrape_jobs(
        self,
        query: str = "software engineer",
        location: str = "United States",
        num_pages: int = 2
    ) -> List[Dict]:

        headers = {
            "X-RapidAPI-Key": self.jsearch_key,
            "X-RapidAPI-Host": self.rapidapi_host,
            "User-Agent": "Mozilla/5.0"
        }

        all_jobs = []

        for page in range(1, num_pages + 1):

            params = {
                "query": query,
                "location": location,
                "page": str(page),
                "num_pages": "1"
            }

            max_retries = 5
            attempt = 0

            while attempt < max_retries:

                try:

                    response = requests.get(
                        self.base_url,
                        headers=headers,
                        params=params,
                        timeout=30
                    )

                    if response.status_code == 200:

                        data = response.json()
                        jobs = data.get("data", [])

                        for job in jobs:
                            processed = self.process_job(job)
                            if processed:
                                all_jobs.append(processed)

                        print(f"✓ Fetched {len(jobs)} jobs from page {page}")
                        break

                    elif response.status_code == 429:
                        print("⚠️ Rate limited. Waiting 10 seconds...")
                        time.sleep(10)

                    elif response.status_code == 403:
                        print("⚠️ Forbidden request. Waiting before retry...")
                        time.sleep(8)

                    else:
                        print(f"❌ Error fetching page {page}: {response.status_code}")
                        break

                except requests.exceptions.Timeout:
                    print("⚠️ Timeout occurred. Retrying in 5 seconds...")
                    time.sleep(5)

                except Exception as e:
                    print(f"❌ Error scraping jobs: {e}")
                    time.sleep(5)

                attempt += 1

            # delay between pages to avoid rate limits
            time.sleep(5)

        return all_jobs

    def process_job(self, raw_job: Dict) -> Optional[Dict]:

        try:

            job_id = raw_job.get("job_id", "")
            if not job_id:
                return None

            description = raw_job.get("job_description", "")

            required_skills = self.extract_skills_from_description(description)

            title = raw_job.get("job_title", "").lower()

            experience_level, min_years, max_years = self.determine_experience_level(
                title,
                description
            )

            min_salary, max_salary = self.parse_salary(raw_job)

            remote_type = self.determine_remote_type(raw_job)

            posted_date = self.parse_date(
                raw_job.get("job_posted_at_datetime_utc")
            )

            deadline = self.estimate_deadline(posted_date)

            return {

                "job_id": job_id,
                "title": raw_job.get("job_title", "Unknown"),
                "company": raw_job.get("employer_name", "Unknown"),
                "company_logo": raw_job.get("employer_logo"),
                "industry": raw_job.get("job_employment_type", "Technology"),
                "description": description,
                "required_skills": required_skills[:10],
                "preferred_skills": required_skills[10:15],
                "experience_level": experience_level,
                "min_years_experience": min_years,
                "max_years_experience": max_years,
                "education": self.extract_education_requirement(description),
                "location": f"{raw_job.get('job_city','')}, {raw_job.get('job_state','')}",
                "remote_type": remote_type,
                "min_salary": min_salary,
                "max_salary": max_salary,
                "employment_type": raw_job.get("job_employment_type", "FULLTIME"),
                "posted_date": posted_date,
                "application_deadline": deadline,
                "url": raw_job.get("job_apply_link", ""),
                "source": "JSearch"
            }

        except Exception as e:
            print(f"Error processing job: {e}")
            return None

    def extract_skills_from_description(self, description: str) -> List[str]:

        skills = [
            "Python","Java","JavaScript","TypeScript","C++","C#","Go",
            "React","Angular","Vue","Node.js","Django","Flask","FastAPI",
            "AWS","Azure","GCP","Docker","Kubernetes",
            "SQL","PostgreSQL","MongoDB",
            "Machine Learning","Deep Learning","TensorFlow","PyTorch",
            "Data Science","Pandas","NumPy","Linux","Git","CI/CD"
        ]

        description = description.lower()

        return [s for s in skills if s.lower() in description]

    def determine_experience_level(self, title: str, description: str):

        text = (title + " " + description).lower()

        if any(w in text for w in ["senior","lead","principal"]):
            return "Senior", 5, 10

        if any(w in text for w in ["junior","entry","graduate"]):
            return "Junior", 0, 2

        return "Mid-Level", 2, 5

    def parse_salary(self, job: Dict):

        return job.get("job_min_salary"), job.get("job_max_salary")

    def determine_remote_type(self, job: Dict):

        if job.get("job_is_remote"):
            return "Remote"

        text = (job.get("job_title","")+job.get("job_description","")).lower()

        if "hybrid" in text:
            return "Hybrid"

        if "remote" in text:
            return "Remote"

        return "Onsite"

    def parse_date(self, date_string):

        if not date_string:
            return datetime.now()

        try:
            return datetime.fromisoformat(date_string.replace("Z","+00:00"))
        except:
            return datetime.now()

    def estimate_deadline(self, posted_date):

        return posted_date + timedelta(days=30)

    def extract_education_requirement(self, description):

        text = description.lower()

        if "phd" in text:
            return "PhD"

        if "master" in text:
            return "Master's Degree"

        if "bachelor" in text:
            return "Bachelor's Degree"

        return None

    async def scrape_and_store_jobs(self):

        queries = [
            "software engineer",
            "data scientist",
            "machine learning engineer"
        ]

        all_jobs = []

        for q in queries:

            print(f"📥 Scraping: {q}")

            jobs = await self.scrape_jobs(q, num_pages=2)

            all_jobs.extend(jobs)

            # delay between queries
            time.sleep(6)

        import pandas as pd

        os.makedirs("data/processed", exist_ok=True)

        df = pd.DataFrame(all_jobs)

        df.to_csv("data/processed/jobs_dataset.csv", index=False)

        print(f"✅ Scraped and saved {len(all_jobs)} jobs")

        return all_jobs