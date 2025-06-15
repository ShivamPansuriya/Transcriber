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

# Configure logging and restart prevention
from logging_config import setup_logging, log_step, log_success, log_error, log_info, log_progress_summary
from restart_handler import setup_restart_prevention, apply_optimal_settings, check_service_health

# Apply optimal settings for the environment
apply_optimal_settings()

# Setup logging (can be controlled via environment variable)
log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
setup_logging(level=log_level, log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true")
logger = logging.getLogger(__name__)

# Setup restart prevention
setup_restart_prevention()

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
    logger.info("🚀 Starting Video Transcription Service")
    logger.info("=" * 50)
    logger.info("📋 Service Configuration:")
    logger.info(f"   🤖 Whisper Model: {settings.WHISPER_MODEL}")
    logger.info(f"   📏 Max File Size: {settings.MAX_FILE_SIZE // (1024*1024)}MB")
    logger.info(f"   🕒 Cleanup Interval: {settings.CLEANUP_INTERVAL_HOURS} hours")
    logger.info(f"   🚦 Rate Limit: {settings.RATE_LIMIT_REQUESTS} requests/minute")
    logger.info(f"   🌐 Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"   📁 Supported Formats: {', '.join(settings.ALLOWED_EXTENSIONS)}")
    logger.info(f"   ⚡ Model Preload: {settings.MODEL_PRELOAD}")
    logger.info("=" * 50)

    log_step("Initializing storage cleanup task")
    await storage.start_cleanup_task()

    # Preload Whisper model to avoid request timeouts
    if settings.MODEL_PRELOAD:
        log_step("Preloading Whisper model (prevents request timeouts)")
        model_loaded = await transcription_service.preload_model()
        if model_loaded:
            log_success("Whisper model preloaded successfully")
        else:
            logger.warning("⚠️ Model preload failed - will try to load during requests")
    else:
        logger.info("⚠️ Model preload disabled - will load during first request")

    log_success("Service startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Video Transcription Service")
    log_step("Stopping cleanup task")
    await storage.stop_cleanup_task()
    log_success("Service shutdown completed")

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    logger.info(f"📁 Validating file: {file.filename}")

    if not file.filename:
        logger.error("❌ No filename provided")
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    logger.info(f"🔍 File extension: {file_ext}")

    if file_ext not in settings.ALLOWED_EXTENSIONS:
        logger.error(f"❌ Unsupported file format: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    logger.info(f"✅ File format validation passed: {file_ext}")

async def validate_file_size(file: UploadFile) -> bytes:
    """Validate file size and return content"""
    logger.info(f"📊 Reading file content for size validation...")
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)

    logger.info(f"📏 File size: {file_size_mb:.2f}MB (max: {max_size_mb}MB)")

    if len(content) > settings.MAX_FILE_SIZE:
        logger.error(f"❌ File too large: {file_size_mb:.2f}MB > {max_size_mb}MB")
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size_mb}MB"
        )

    if len(content) == 0:
        logger.error("❌ Empty file detected")
        raise HTTPException(status_code=400, detail="Empty file")

    logger.info(f"✅ File size validation passed: {file_size_mb:.2f}MB")
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
        logger.info(f"🚀 Starting transcription request for file: {file.filename}")
        logger.info(f"🌐 Language specified: {language or 'auto-detect'}")

        # Validate file
        validate_file(file)

        # Read and validate file content
        content = await validate_file_size(file)

        # Create transcription entry
        logger.info("📝 Creating transcription entry in storage...")
        transcription_id = storage.create_transcription(language=language)
        logger.info(f"🆔 Transcription ID created: {transcription_id}")

        # Start transcription in background
        logger.info(f"⚡ Starting background transcription task for ID: {transcription_id}")
        asyncio.create_task(
            transcription_service.transcribe_video(content, transcription_id, language)
        )

        logger.info(f"✅ Transcription request accepted successfully - ID: {transcription_id}")
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
        logger.info(f"🔍 Looking up transcription ID: {transcription_id}")
        result = storage.get_transcription(transcription_id)

        if not result:
            logger.warning(f"❌ Transcription not found: {transcription_id}")
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    id=0,
                    error="not_found",
                    message="Transcription not found or expired"
                ).dict()
            )

        logger.info(f"📊 Transcription status for ID {transcription_id}: {result.status}")
        if result.status == TranscriptionStatus.COMPLETED:
            text_preview = result.text[:100] + "..." if result.text and len(result.text) > 100 else result.text
            logger.info(f"✅ Transcription completed - Preview: {text_preview}")
        elif result.status == TranscriptionStatus.FAILED:
            logger.error(f"❌ Transcription failed for ID {transcription_id}: {result.error_message}")

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
    # Check model status
    model_status = "not_loaded"
    if transcription_service._model is not None:
        model_status = "loaded"
    elif transcription_service._model_loading:
        model_status = "loading"
    elif transcription_service._model_load_error:
        model_status = "error"

    active_transcriptions = 0
    total_transcriptions = 0

    if hasattr(storage, '_storage'):
        total_transcriptions = len(storage._storage)
        active_transcriptions = len([
            t for t in storage._storage.values()
            if t.status in [TranscriptionStatus.PENDING, TranscriptionStatus.PROCESSING]
        ])

    return {
        "status": "healthy" if model_status in ["loaded", "loading"] else "degraded",
        "model_status": model_status,
        "model_name": settings.WHISPER_MODEL,
        "model_error": transcription_service._model_load_error,
        "total_transcriptions": total_transcriptions,
        "active_transcriptions": active_transcriptions,
        "max_file_size_mb": settings.MAX_FILE_SIZE // (1024*1024),
        "supported_formats": settings.ALLOWED_EXTENSIONS,
        "uptime_check": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
