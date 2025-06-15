from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import os
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from models import (
    TranscriptionRequest, TranscriptionResponse, TranscriptionResult, 
    ErrorResponse, TranscriptionStatus
)
from storage import storage
from transcription_service import transcription_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Video Transcription Service",
    description="A free video transcription service using OpenAI Whisper",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Video Transcription Service")
    await storage.start_cleanup_task()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Video Transcription Service")
    await storage.stop_cleanup_task()

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

async def validate_file_size(file: UploadFile) -> bytes:
    """Validate file size and return content"""
    content = await file.read()
    
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    return content

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Video Transcription Service",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/transcribe", response_model=TranscriptionResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/minute")
async def transcribe_video(
    request: Request,
    file: UploadFile = File(...),
    language: str = None
):
    """
    Upload a video file for transcription
    
    - **file**: Video file (MP4, AVI, MOV, etc.) - Max 100MB
    - **language**: Optional language code (e.g., 'en', 'es', 'fr') - Auto-detect if not provided
    
    Returns transcription ID for status checking
    """
    try:
        # Validate file
        validate_file(file)
        
        # Read and validate file content
        content = await validate_file_size(file)
        
        # Create transcription entry
        transcription_id = storage.create_transcription(language=language)
        
        # Start transcription in background
        asyncio.create_task(
            transcription_service.transcribe_video(content, transcription_id, language)
        )
        
        return TranscriptionResponse(
            id=transcription_id,
            status=TranscriptionStatus.PENDING,
            message="Transcription started. Use the ID to check status.",
            created_at=storage.get_transcription(transcription_id).created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                id=0,
                error="internal_error",
                message="An internal error occurred"
            ).dict()
        )

@app.get("/transcribe/{transcription_id}", response_model=TranscriptionResult)
async def get_transcription(transcription_id: int):
    """
    Get transcription status and results
    
    - **transcription_id**: ID returned from the transcribe endpoint
    
    Returns transcription status and text (if completed)
    """
    try:
        result = storage.get_transcription(transcription_id)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    id=0,
                    error="not_found",
                    message="Transcription not found or expired"
                ).dict()
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_transcription endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                id=0,
                error="internal_error",
                message="An internal error occurred"
            ).dict()
        )

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": storage._storage.__len__() if hasattr(storage, '_storage') else 0,
        "active_transcriptions": len([
            t for t in storage._storage.values() 
            if t.status in [TranscriptionStatus.PENDING, TranscriptionStatus.PROCESSING]
        ]) if hasattr(storage, '_storage') else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
