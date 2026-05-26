import os
import requests
from typing import Optional

JSEARCH_API_KEY = "8987c3a608msh62942bfa3fa65c4p131771jsnadd3fe51d6a4"
JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": JSEARCH_API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com",
}


def fetch_jobs_for_resume(parsed_resume: dict, max_jobs: int = 50) -> list:
    queries = _build_search_queries(parsed_resume)
    all_jobs = []
    seen_ids = set()

    for query in queries:
        try:
            jobs = _fetch_jsearch_jobs(query)
            for job in jobs:
                job_id = job.get("job_id") or job.get("job_apply_link", "")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    normalized = _normalize_job(job)
                    if normalized:
                        all_jobs.append(normalized)
        except Exception as e:
            print(f"[job_fetcher] JSearch query failed: {e}")
            continue

        if len(all_jobs) >= max_jobs:
            break

    if not all_jobs:
        print("[job_fetcher] JSearch returned no results, using demo data")
        return _get_demo_jobs(parsed_resume)

    return all_jobs[:max_jobs]


def _build_search_queries(resume: dict) -> list:
    queries = []
    title = resume.get("current_title", "Software Engineer")
    location = resume.get("location", "")
    skills = resume.get("technical_skills", [])[:3]
    seniority = resume.get("seniority_level", "mid")

    seniority_prefix = {
        "senior": "Senior", "lead": "Lead",
        "junior": "Junior", "executive": "Director",
    }.get(seniority, "")

    q1 = f"{seniority_prefix} {title}".strip()
    queries.append({"query": q1, "location": location})

    if skills:
        queries.append({"query": f"{skills[0]} {title}", "location": location})

    queries.append({"query": title, "location": "remote", "remote_jobs_only": True})

    return queries


def _fetch_jsearch_jobs(params: dict) -> list:
    query = params.get("query", "Software Engineer")
    location = params.get("location", "")
    remote_only = params.get("remote_jobs_only", False)

    full_query = query
    if location and not remote_only:
        full_query = f"{query} in {location}"

    querystring = {
        "query": full_query,
        "page": "1",
        "num_pages": "2",
        "date_posted": "month",
    }
    if remote_only:
        querystring["remote_jobs_only"] = "true"

    response = requests.get(
        f"{JSEARCH_BASE_URL}/search",
        headers=HEADERS,
        params=querystring,
        timeout=15,
    )

    if response.status_code == 200:
        return response.json().get("data", [])
    elif response.status_code == 429:
        raise Exception("JSearch rate limit hit")
    elif response.status_code == 403:
        raise Exception("JSearch API key invalid")
    else:
        raise Exception(f"JSearch error {response.status_code}")


def _normalize_job(raw: dict) -> Optional[dict]:
    title = (raw.get("job_title") or "").strip()
    if not title:
        return None

    company = (raw.get("employer_name") or "Unknown Company").strip()

    city = raw.get("job_city") or ""
    state = raw.get("job_state") or ""
    country = raw.get("job_country") or ""
    is_remote = raw.get("job_is_remote", False)

    if is_remote:
        location = "Remote"
    elif city and state:
        location = f"{city}, {state}"
    elif city:
        location = city
    else:
        location = country or "Not specified"

    description = raw.get("job_description") or ""
    apply_url = raw.get("job_apply_link") or ""

    publisher = (raw.get("job_publisher") or "").lower()
    indeed_url = apply_url if "indeed" in publisher else ""
    linkedin_url = apply_url if "linkedin" in publisher else ""

    salary = ""
    min_sal = raw.get("job_min_salary")
    max_sal = raw.get("job_max_salary")
    sal_currency = raw.get("job_salary_currency") or "USD"
    if min_sal and max_sal:
        salary = f"{sal_currency} {int(min_sal):,} - {int(max_sal):,}"
    elif min_sal:
        salary = f"{sal_currency} {int(min_sal):,}+"

    highlights = raw.get("job_highlights") or {}
    qual_text = " ".join(highlights.get("Qualifications", []))
    required_skills = list(set(
        _extract_skills_from_text(description) +
        _extract_skills_from_text(qual_text)
    ))[:15]

    min_years, max_years = _parse_experience(qual_text)
    seniority = _infer_seniority(title)
    job_type = "Remote" if is_remote else _normalize_job_type(raw.get("job_employment_type") or "FULLTIME")

    return {
        "id": raw.get("job_id") or str(hash(title + company)),
        "title": title,
        "company": company,
        "location": location,
        "description": description[:1500],
        "required_skills": required_skills,
        "preferred_skills": [],
        "salary": salary,
        "job_type": job_type,
        "posted_date": raw.get("job_posted_at_datetime_utc") or "",
        "apply_url": apply_url,
        "indeed_apply_url": indeed_url,
        "linkedin_apply_url": linkedin_url,
        "company_logo": raw.get("employer_logo") or "",
        "min_years_experience": min_years,
        "max_years_experience": max_years,
        "seniority_level": seniority,
        "source": "jsearch",
        "publisher": raw.get("job_publisher") or "",
    }


def _extract_skills_from_text(text: str) -> list:
    if not text:
        return []
    text_lower = text.lower()
    known_skills = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala",
        "react", "vue", "angular", "next.js", "svelte", "html", "css", "tailwind",
        "node.js", "django", "fastapi", "flask", "spring", "express",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd",
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "graphql", "rest api", "microservices", "git", "linux", "agile",
        "machine learning", "deep learning", "nlp", "sql", "tableau", "power bi",
    ]
    return [s for s in known_skills if s in text_lower][:15]


def _parse_experience(text: str) -> tuple:
    import re
    if not text:
        return (1, 5)
    numbers = re.findall(r'\d+', text)
    if len(numbers) >= 2:
        return (int(numbers[0]), int(numbers[1]))
    elif len(numbers) == 1:
        n = int(numbers[0])
        return (n, n + 3)
    return (2, 5)


def _infer_seniority(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["vp ", "director", "cto", "ceo", "head of"]):
        return "executive"
    elif any(w in t for w in ["lead", "principal", "staff", "architect"]):
        return "lead"
    elif "senior" in t or "sr." in t or "sr " in t:
        return "senior"
    elif any(w in t for w in ["junior", "jr.", "entry", "associate", "intern"]):
        return "junior"
    return "mid"


def _normalize_job_type(emp_type: str) -> str:
    t = emp_type.upper()
    if "PART" in t: return "Part-time"
    if "CONTRACT" in t: return "Contract"
    if "INTERN" in t: return "Internship"
    return "Full-time"


def _get_demo_jobs(resume: dict) -> list:
    title = resume.get("current_title", "Software Engineer")
    skills = resume.get("technical_skills", ["Python", "JavaScript"])[:4]
    seniority = resume.get("seniority_level", "mid")
    level_prefix = {"senior": "Senior ", "lead": "Lead ", "junior": "Junior "}.get(seniority, "")

    companies = [
        ("Google", "Mountain View, CA", "https://careers.google.com"),
        ("Meta", "Remote", "https://www.metacareers.com"),
        ("Stripe", "Remote / SF", "https://stripe.com/jobs"),
        ("Shopify", "Remote", "https://www.shopify.com/careers"),
        ("Airbnb", "San Francisco, CA", "https://careers.airbnb.com"),
        ("Notion", "Remote", "https://www.notion.so/careers"),
        ("Vercel", "Remote", "https://vercel.com/careers"),
        ("Linear", "Remote", "https://linear.app/careers"),
    ]

    return [
        {
            "id": f"demo_{i}",
            "title": f"{level_prefix}{title}",
            "company": company,
            "location": location,
            "description": (
                f"We are looking for a talented {title} to join our team. "
                f"You will work with {', '.join(skills)} and collaborate with "
                f"cross-functional teams to build world-class products."
            ),
            "required_skills": skills,
            "preferred_skills": [],
            "salary": f"${120 + i * 10:,} - ${160 + i * 10:,}",
            "job_type": "Remote" if "Remote" in location else "Full-time",
            "posted_date": "2026-03-11",
            "apply_url": apply_url,
            "indeed_apply_url": "",
            "linkedin_apply_url": "",
            "company_logo": "",
            "min_years_experience": 2,
            "max_years_experience": 7,
            "seniority_level": seniority,
            "source": "demo",
            "publisher": "Demo",
        }
        for i, (company, location, apply_url) in enumerate(companies)
    ]