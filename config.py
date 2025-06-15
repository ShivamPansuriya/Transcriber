import os
from typing import List

class Settings:
    # File upload settings
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for free tier
    ALLOWED_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    
    # Transcription settings
    WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
    CLEANUP_INTERVAL_HOURS = 3.5  # Clean up after 3.5 hours
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 10  # requests per minute per IP
    
    # Server settings
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))
    
    # Render.com specific
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")

settings = Settings()
