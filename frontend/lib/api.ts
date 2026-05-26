const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ResumeData {
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  current_title?: string;
  years_experience?: number;
  skills?: string[];
  technical_skills?: string[];
  soft_skills?: string[];
  seniority_level?: string;
  education?: Array<{
    degree: string;
    field: string;
    institution: string;
    year: string;
  }>;
  experience?: Array<{
    title: string;
    company: string;
    duration: string;
    years: number;
    responsibilities: string[];
    technologies: string[];
  }>;
}

export interface JobMatch {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  required_skills: string[];
  salary?: string;
  job_type?: string;
  posted_date?: string;
  apply_url: string;
  indeed_apply_url?: string;
  linkedin_apply_url?: string;
  company_logo?: string;
  seniority_level?: string;
  // Scores
  overall_score: number;
  semantic_score: number;
  skill_match_score: number;
  experience_score: number;
  location_score: number;
  match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  explanation: string;
  source?: string;
}

export interface UploadResponse {
  success: boolean;
  file_id: string;
  filename: string;
  resume: ResumeData;
  matches: JobMatch[];
  total_jobs_searched: number;
  message: string;
}

export interface ApiError {
  detail: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err: ApiError = await res.json();
      detail = err.detail || detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadResume(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<UploadResponse>(res);
}

export async function getHealth(): Promise<{ status: string; anthropic_configured: boolean }> {
  const res = await fetch(`${API_URL}/health`);
  return handleResponse(res);
}

export async function searchJobs(query: string, location?: string): Promise<{ jobs: JobMatch[] }> {
  const params = new URLSearchParams({ query });
  if (location) params.append("location", location);

  const res = await fetch(`${API_URL}/jobs?${params}`);
  return handleResponse(res);
}