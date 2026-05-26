import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="JobMatch AI",
    description="Semantic resume-to-job matching with Claude RAG",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import upload, matching, jobs

app.include_router(upload.router)
app.include_router(matching.router)
app.include_router(jobs.router)


@app.get("/")
async def root():
    return {
        "service": "JobMatch AI",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    anthropic_ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "status": "ok",
        "anthropic_configured": anthropic_ok,
        "model": "claude-sonnet-4-20250514",
    }