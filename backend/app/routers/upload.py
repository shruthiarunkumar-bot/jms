import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf", ".doc", ".docx",
    # Images (phone photos, scans)
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif"
}

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB (images can be large)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume (PDF, DOCX, or image) and run full matching pipeline."""

    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Accepted: PDF, DOCX, PNG, JPG, JPEG, WEBP, BMP, TIFF"
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 15MB.")
    if len(content) < 100:
        raise HTTPException(status_code=400, detail="File appears empty or corrupted.")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        from app.services.ai_matcher import full_match_pipeline
        result = full_match_pipeline(file_path, top_k=10)

        return JSONResponse(content={
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "resume": result["resume"],
            "matches": result["matches"],
            "total_jobs_searched": result["total_jobs_searched"],
            "message": f"Found {len(result['matches'])} matches from {result['total_jobs_searched']} listings"
        })

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "JobMatch AI"}