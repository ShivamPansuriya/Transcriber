#!/usr/bin/env python3
"""
Robust startup script for Video Transcription Service
Handles restarts and optimizes for free tier hosting
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def detect_environment():
    """Detect if running on Render.com or locally"""
    if os.getenv("RENDER"):
        return "render"
    elif os.getenv("PORT"):
        return "cloud"
    else:
        return "local"

def get_optimal_env_vars():
    """Get optimal environment variables for the detected environment"""
    env = detect_environment()
    
    base_vars = {
        "PYTHONUNBUFFERED": "1",
        "MODEL_PRELOAD": "true"
    }
    
    if env == "render":
        logger.info("🌐 Detected Render.com environment")
        base_vars.update({
            "WHISPER_MODEL": "tiny",  # Faster loading, less memory
            "DEBUG": "false",         # Reduce log overhead
            "LOG_TO_FILE": "false"    # No file logging on Render
        })
    elif env == "cloud":
        logger.info("☁️ Detected cloud environment")
        base_vars.update({
            "WHISPER_MODEL": "tiny",
            "DEBUG": "false"
        })
    else:
        logger.info("💻 Detected local environment")
        base_vars.update({
            "WHISPER_MODEL": os.getenv("WHISPER_MODEL", "base"),
            "DEBUG": os.getenv("DEBUG", "true")
        })
    
    return base_vars

def preload_model():
    """Preload the Whisper model to avoid request timeouts"""
    try:
        logger.info("🤖 Preloading Whisper model...")
        
        # Import and load model
        import whisper
        model_name = os.getenv("WHISPER_MODEL", "tiny")
        
        start_time = time.time()
        model = whisper.load_model(model_name)
        load_time = time.time() - start_time
        
        logger.info(f"✅ Model '{model_name}' preloaded in {load_time:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model preload failed: {e}")
        return False

def start_service():
    """Start the FastAPI service with optimal settings"""
    env_vars = get_optimal_env_vars()
    
    # Set environment variables
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"⚙️ Set {key}={value}")
    
    # Log configuration
    logger.info("📋 Service Configuration:")
    logger.info(f"   🤖 Whisper Model: {os.getenv('WHISPER_MODEL', 'base')}")
    logger.info(f"   🔧 Debug Mode: {os.getenv('DEBUG', 'false')}")
    logger.info(f"   📥 Model Preload: {os.getenv('MODEL_PRELOAD', 'true')}")
    logger.info(f"   🌐 Port: {os.getenv('PORT', '8000')}")
    
    # Preload model if enabled
    if os.getenv("MODEL_PRELOAD", "true").lower() == "true":
        if not preload_model():
            logger.warning("⚠️ Continuing without model preload...")
    
    # Start the service
    try:
        logger.info("🚀 Starting FastAPI service...")
        
        # Use uvicorn directly
        import uvicorn
        from main import app
        
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import whisper
        import torch
        logger.info("✅ Core dependencies available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Run: pip install -r requirements.txt")
        return False

def main():
    logger.info("🚀 Video Transcription Service - Robust Startup")
    logger.info("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start service
    start_service()

if __name__ == "__main__":
    main()
