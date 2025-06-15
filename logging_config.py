"""
Logging configuration for Video Transcription Service
"""

import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO, log_to_file=False):
    """
    Setup comprehensive logging for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to also log to a file
    """
    
    # Create formatter with emojis and detailed info
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    handlers = [console_handler]
    
    # Setup file handler if requested
    if log_to_file:
        log_filename = f"transcription_service_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Set specific logger levels
    loggers = [
        'main',
        'transcription_service', 
        'storage',
        'uvicorn.access',
        'uvicorn.error'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Reduce noise from some third-party libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_progress_logger():
    """Get a logger specifically for progress tracking"""
    logger = logging.getLogger('progress')
    logger.setLevel(logging.INFO)
    return logger

# Progress tracking functions
def log_step(step_name: str, transcription_id: int = None):
    """Log a processing step"""
    logger = get_progress_logger()
    if transcription_id:
        logger.info(f"🔄 [{transcription_id}] {step_name}")
    else:
        logger.info(f"🔄 {step_name}")

def log_success(message: str, transcription_id: int = None):
    """Log a success message"""
    logger = get_progress_logger()
    if transcription_id:
        logger.info(f"✅ [{transcription_id}] {message}")
    else:
        logger.info(f"✅ {message}")

def log_error(message: str, transcription_id: int = None):
    """Log an error message"""
    logger = get_progress_logger()
    if transcription_id:
        logger.error(f"❌ [{transcription_id}] {message}")
    else:
        logger.error(f"❌ {message}")

def log_warning(message: str, transcription_id: int = None):
    """Log a warning message"""
    logger = get_progress_logger()
    if transcription_id:
        logger.warning(f"⚠️ [{transcription_id}] {message}")
    else:
        logger.warning(f"⚠️ {message}")

def log_info(message: str, transcription_id: int = None):
    """Log an info message"""
    logger = get_progress_logger()
    if transcription_id:
        logger.info(f"ℹ️ [{transcription_id}] {message}")
    else:
        logger.info(f"ℹ️ {message}")

def log_progress_summary(transcription_id: int, total_time: float, status: str):
    """Log a summary of transcription progress"""
    logger = get_progress_logger()
    logger.info(f"📊 [{transcription_id}] SUMMARY:")
    logger.info(f"   Status: {status}")
    logger.info(f"   Total Time: {total_time:.2f} seconds")
    logger.info(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Example usage and testing
if __name__ == "__main__":
    # Test the logging configuration
    setup_logging(level=logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing logging configuration...")
    
    # Test progress logging
    log_step("Starting test transcription", 123)
    log_info("Processing video file", 123)
    log_success("Audio extraction completed", 123)
    log_warning("Large file detected", 123)
    log_error("Test error message", 123)
    log_progress_summary(123, 45.6, "completed")
    
    logger.info("✅ Logging test completed")
