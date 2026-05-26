import os
import json
import base64
import numpy as np
import re
from typing import Optional
import anthropic

_sentence_model = None
_faiss = None


def get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer
        _sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _sentence_model


def get_faiss():
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Supported file types
PDF_EXTS = {'.pdf'}
DOCX_EXTS = {'.doc', '.docx'}
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff', '.tif'}


def extract_resume_text(file_path: str) -> str:
    """
    Extract text from any resume file:
    - PDF: pdfplumber (handles scanned PDFs too via fallback to Claude Vision)
    - DOCX/DOC: python-docx
    - Images (PNG/JPG/etc): Claude Vision OCR
    Returns extracted text string.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in PDF_EXTS:
        return _extract_pdf(file_path)
    elif ext in DOCX_EXTS:
        return _extract_docx(file_path)
    elif ext in IMAGE_EXTS:
        return _extract_image_via_claude(file_path)
    else:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: PDF, DOCX, DOC, PNG, JPG, JPEG, WEBP, GIF, BMP, TIFF"
        )


def _extract_pdf(file_path: str) -> str:
    """Extract text from PDF. Falls back to Claude Vision if text is sparse (scanned PDF)."""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            extracted = "\n".join(pages_text).strip()

        # If very little text extracted, it's likely a scanned/image PDF
        if len(extracted) < 150:
            print("[ai_matcher] PDF has sparse text — trying Claude Vision OCR")
            return _extract_pdf_as_image_via_claude(file_path)

        return extracted

    except Exception as e:
        print(f"[ai_matcher] pdfplumber failed: {e} — trying Claude Vision")
        return _extract_pdf_as_image_via_claude(file_path)


def _extract_pdf_as_image_via_claude(file_path: str) -> str:
    """Send PDF directly to Claude as a document for OCR parsing."""
    try:
        with open(file_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a resume. Extract ALL text content from it exactly as written. "
                            "Include name, contact info, all job titles, companies, dates, responsibilities, "
                            "skills, education, certifications — everything. "
                            "Output only the raw text, no formatting or commentary."
                        )
                    }
                ]
            }]
        )
        return response.content[0].text.strip()

    except Exception as e:
        raise ValueError(f"Claude Vision PDF extraction failed: {e}")


def _extract_docx(file_path: str) -> str:
    """Extract text from DOCX/DOC."""
    try:
        from docx import Document
        doc = Document(file_path)
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text)
        # Also extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    parts.append(row_text)
        return "\n".join(parts).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX: {e}")


def _extract_image_via_claude(file_path: str) -> str:
    """
    Use Claude Vision to OCR a resume image (JPG, PNG, etc).
    Handles blurry, low-res, or phone-photographed resumes.
    """
    ext = os.path.splitext(file_path)[1].lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/jpeg",   # convert BMP as JPEG
        ".tiff": "image/jpeg",
        ".tif": "image/jpeg",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    try:
        with open(file_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "This is a photo or scan of a resume. Even if it's blurry or low quality, "
                            "extract ALL readable text content. Include the person's name, contact details, "
                            "every job title, company, date range, responsibilities, all skills, education, "
                            "certifications, and any other visible text. "
                            "Do your best to read unclear text — make educated guesses for partially visible words. "
                            "Output only the extracted text, no commentary."
                        )
                    }
                ]
            }]
        )
        text = response.content[0].text.strip()
        if len(text) < 50:
            raise ValueError("Extracted text too short — image may be unreadable")
        return text

    except Exception as e:
        raise ValueError(f"Claude Vision image extraction failed: {e}")


def parse_resume_with_claude(resume_text: str) -> dict:
    """Use Claude to extract structured resume data from raw text."""
    prompt = f"""You are a precise resume parser. Extract structured information from the resume text below.

Return ONLY valid JSON with this exact structure:
{{
  "name": "Full Name",
  "email": "email@example.com or null",
  "phone": "phone number or null",
  "location": "City, State/Country or null",
  "summary": "professional summary in 2-3 sentences",
  "current_title": "most recent job title",
  "years_experience": <integer>,
  "skills": ["skill1", "skill2", ...],
  "technical_skills": ["tech1", "tech2", ...],
  "soft_skills": ["communication", ...],
  "education": [
    {{"degree": "...", "field": "...", "institution": "...", "year": "..."}}
  ],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Jan 2020 - Dec 2022",
      "years": 2.0,
      "responsibilities": ["did X", "built Y"],
      "technologies": ["Python", "React"]
    }}
  ],
  "certifications": ["cert1"],
  "languages": ["English"],
  "seniority_level": "junior|mid|senior|lead|executive",
  "preferred_industries": ["tech", "finance"],
  "job_types": ["full-time"],
  "rich_text": "comprehensive 400-500 word narrative combining all experience and skills for semantic search"
}}

The "rich_text" field is CRITICAL — write a dense 400-500 word paragraph combining all job history,
skills, accomplishments, and career goals. This is used for semantic vector search so make it rich.

Resume text:
{resume_text[:6000]}

Return ONLY the JSON, no markdown fences, no explanation."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r'^```json\s*', '', raw)
        raw = re.sub(r'^```\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        return json.loads(raw)
    except Exception as e:
        print(f"[ai_matcher] Claude parse failed: {e} — using fallback")
        return _fallback_parse(resume_text)


def _fallback_parse(text: str) -> dict:
    """Basic regex fallback if Claude parse fails."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    skills = []
    skill_keywords = ['python', 'javascript', 'react', 'node', 'sql', 'java', 'aws',
                      'docker', 'kubernetes', 'typescript', 'vue', 'angular', 'go', 'rust']
    for line in lines:
        for kw in skill_keywords:
            if kw in line.lower():
                skills.append(kw)

    return {
        "name": lines[0] if lines else "Unknown",
        "email": None,
        "phone": None,
        "location": None,
        "summary": text[:300],
        "current_title": "Software Professional",
        "years_experience": 3,
        "skills": list(set(skills))[:20],
        "technical_skills": list(set(skills))[:15],
        "soft_skills": [],
        "education": [],
        "experience": [],
        "certifications": [],
        "languages": ["English"],
        "seniority_level": "mid",
        "preferred_industries": [],
        "job_types": ["full-time"],
        "rich_text": text[:1000],
    }


def embed_text(text: str) -> np.ndarray:
    model = get_sentence_model()
    embedding = model.encode([text], normalize_embeddings=True)
    return embedding[0].astype(np.float32)


def embed_resume(parsed_resume: dict) -> np.ndarray:
    skills_str = " ".join(parsed_resume.get("skills", []))
    tech_str = " ".join(parsed_resume.get("technical_skills", []))

    exp_str = ""
    for exp in parsed_resume.get("experience", [])[:3]:
        exp_str += f"{exp.get('title','')} at {exp.get('company','')}. "
        exp_str += " ".join(exp.get("responsibilities", [])[:3]) + " "

    combined = f"""
    {parsed_resume.get('rich_text', '')}
    Skills: {skills_str}
    Technical expertise: {tech_str}
    Work history: {exp_str}
    Level: {parsed_resume.get('seniority_level', 'mid')}
    Title: {parsed_resume.get('current_title', '')}
    """.strip()

    return embed_text(combined)


def embed_job(job: dict) -> np.ndarray:
    job_text = f"""
    {job.get('title', '')} at {job.get('company', '')}
    Location: {job.get('location', '')}
    {job.get('description', '')}
    Required skills: {' '.join(job.get('required_skills', []))}
    Experience: {job.get('min_years_experience', 0)}-{job.get('max_years_experience', 5)} years
    Type: {job.get('job_type', '')}
    """.strip()
    return embed_text(job_text)


def semantic_match_jobs(resume_vector: np.ndarray, jobs: list, top_k: int = 10) -> list:
    faiss = get_faiss()

    if not jobs:
        return []

    dimension = resume_vector.shape[0]
    index = faiss.IndexFlatIP(dimension)

    job_vectors = []
    valid_jobs = []

    for job in jobs:
        try:
            vec = embed_job(job)
            job_vectors.append(vec)
            valid_jobs.append(job)
        except Exception:
            continue

    if not job_vectors:
        return []

    matrix = np.array(job_vectors, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    matrix = matrix / norms

    index.add(matrix)

    query = resume_vector.reshape(1, -1)
    qnorm = np.linalg.norm(query)
    if qnorm > 0:
        query = query / qnorm

    k = min(top_k, len(valid_jobs))
    scores, indices = index.search(query, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        job = valid_jobs[idx].copy()
        job['semantic_score'] = float(score)
        results.append(job)

    return results


def compute_granular_score(resume: dict, job: dict, semantic_score: float) -> dict:
    resume_skills = set(
        s.lower() for s in resume.get("skills", []) + resume.get("technical_skills", [])
    )
    job_skills = set(
        s.lower() for s in job.get("required_skills", []) + job.get("preferred_skills", [])
    )

    skill_overlap = len(resume_skills & job_skills) / len(job_skills) if job_skills else 0.5

    resume_years = resume.get("years_experience", 0)
    job_min = job.get("min_years_experience", 0)
    job_max = job.get("max_years_experience", 10)

    if job_min <= resume_years <= job_max:
        exp_score = 1.0
    elif resume_years > job_max:
        exp_score = 0.7
    else:
        exp_score = max(0, 1.0 - ((job_min - resume_years) * 0.2))

    resume_loc = (resume.get("location") or "").lower()
    job_loc = (job.get("location") or "").lower()
    if "remote" in job_loc or "remote" in (job.get("job_type") or "").lower():
        location_score = 1.0
    elif resume_loc and any(w in job_loc for w in resume_loc.split(", ") if len(w) > 2):
        location_score = 1.0
    else:
        location_score = 0.5

    seniority_map = {"junior": 1, "mid": 2, "senior": 3, "lead": 4, "executive": 5}
    r_level = seniority_map.get(resume.get("seniority_level", "mid"), 2)
    j_level = seniority_map.get(job.get("seniority_level", "mid"), 2)
    seniority_score = max(0.2, 1.0 - abs(r_level - j_level) * 0.2)

    final = (
        semantic_score * 0.40 +
        skill_overlap * 0.30 +
        exp_score * 0.15 +
        location_score * 0.10 +
        seniority_score * 0.05
    )

    return {
        "overall_score": round(final * 100, 1),
        "semantic_score": round(semantic_score * 100, 1),
        "skill_match_score": round(skill_overlap * 100, 1),
        "experience_score": round(exp_score * 100, 1),
        "location_score": round(location_score * 100, 1),
        "matched_skills": list(resume_skills & job_skills)[:10],
        "missing_skills": list(job_skills - resume_skills)[:5],
        "match_percentage": round(final * 100),
    }


def generate_match_explanation(resume: dict, job: dict, scores: dict) -> str:
    try:
        prompt = f"""You are a career advisor. Write a concise, specific 3-sentence explanation of why this candidate matches this job.

Candidate: {resume.get('name', 'Candidate')}
Title: {resume.get('current_title', 'Professional')}
Key Skills: {', '.join(resume.get('technical_skills', [])[:8])}
Years Experience: {resume.get('years_experience', 0)}
Level: {resume.get('seniority_level', 'mid')}

Job: {job.get('title', 'Position')} at {job.get('company', 'Company')}
Required Skills: {', '.join(job.get('required_skills', [])[:8])}
Location: {job.get('location', 'Not specified')}

Match: {scores['overall_score']}% overall, {scores['skill_match_score']}% skill match
Matched skills: {', '.join(scores.get('matched_skills', [])[:5])}
Missing: {', '.join(scores.get('missing_skills', [])[:3])}

Write exactly 3 sentences:
1. Why their background fits this role (mention specific skills)
2. What stands out or a gap to address
3. One actionable tip for applying

Be specific — reference actual skills and titles. No generic filler."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception:
        matched = scores.get('matched_skills', [])[:3]
        return (
            f"Your {resume.get('current_title', 'background')} aligns well with the "
            f"{job.get('title', 'role')} requirements"
            + (f", particularly your experience with {', '.join(matched)}." if matched else ".")
            + f" This role matches your {resume.get('seniority_level', 'experience')} level profile. "
            f"Highlight your most relevant projects and quantify your impact when applying."
        )


def full_match_pipeline(file_path: str, top_k: int = 10) -> dict:
    """End-to-end: file → text extraction → parse → embed → match → explain."""

    # Step 1: Extract text (handles PDF, DOCX, images, scanned docs)
    resume_text = extract_resume_text(file_path)
    if not resume_text or len(resume_text) < 30:
        raise ValueError("Could not extract readable text from resume. Try a clearer image or PDF.")

    # Step 2: Parse with Claude
    parsed_resume = parse_resume_with_claude(resume_text)

    # Step 3: Embed
    resume_vector = embed_resume(parsed_resume)

    # Step 4: Fetch jobs
    from .job_fetcher import fetch_jobs_for_resume
    jobs = fetch_jobs_for_resume(parsed_resume)

    if not jobs:
        raise ValueError("No jobs found. Check API connectivity.")

    # Step 5: Semantic match
    matched = semantic_match_jobs(resume_vector, jobs, top_k=top_k * 2)

    # Step 6: Score + explain
    results = []
    for job in matched[:top_k]:
        scores = compute_granular_score(parsed_resume, job, job.get('semantic_score', 0.5))
        explanation = generate_match_explanation(parsed_resume, job, scores)
        results.append({**job, **scores, "explanation": explanation})

    results.sort(key=lambda x: x['overall_score'], reverse=True)

    return {
        "resume": parsed_resume,
        "matches": results,
        "total_jobs_searched": len(jobs),
    }