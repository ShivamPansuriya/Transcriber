#!/usr/bin/env python3
"""
Restart handler for Video Transcription Service
Helps prevent restarts due to memory/timeout issues
"""

import os
import signal
import sys
import time
import logging
import psutil
from datetime import datetime

logger = logging.getLogger(__name__)

class RestartHandler:
    def __init__(self):
        self.start_time = time.time()
        self.restart_count = 0
        self.memory_warnings = 0
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        
        # Log service statistics
        uptime = time.time() - self.start_time
        logger.info(f"📊 Service uptime: {uptime:.1f} seconds")
        logger.info(f"🔄 Restart count: {self.restart_count}")
        logger.info(f"⚠️ Memory warnings: {self.memory_warnings}")
        
        sys.exit(0)
    
    def check_memory_usage(self):
        """Check memory usage and warn if high"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            # Warn if using more than 400MB (80% of 512MB limit)
            if memory_mb > 400:
                self.memory_warnings += 1
                logger.warning(f"⚠️ High memory usage: {memory_mb:.1f}MB (limit: 512MB)")
                logger.warning("💡 Consider using 'tiny' model or smaller files")
                return True
            elif memory_mb > 300:
                logger.info(f"📊 Memory usage: {memory_mb:.1f}MB")
                
            return False
        except Exception as e:
            logger.error(f"❌ Error checking memory: {e}")
            return False
    
    def log_system_info(self):
        """Log system information for debugging"""
        try:
            logger.info("🖥️ System Information:")
            logger.info(f"   Python: {sys.version.split()[0]}")
            logger.info(f"   Platform: {sys.platform}")
            
            if hasattr(psutil, 'virtual_memory'):
                memory = psutil.virtual_memory()
                logger.info(f"   Total Memory: {memory.total / (1024**3):.1f}GB")
                logger.info(f"   Available Memory: {memory.available / (1024**3):.1f}GB")
            
            if hasattr(psutil, 'cpu_count'):
                logger.info(f"   CPU Cores: {psutil.cpu_count()}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not get system info: {e}")
    
    def create_restart_prevention_tips(self):
        """Create tips to prevent restarts"""
        tips = [
            "🔧 Restart Prevention Tips:",
            "1. Use WHISPER_MODEL=tiny for faster loading and less memory",
            "2. Keep video files under 50MB for free tier",
            "3. Process one video at a time",
            "4. Enable model preloading: MODEL_PRELOAD=true",
            "5. Monitor memory usage in logs",
            "6. Use DEBUG=false in production to reduce log overhead"
        ]
        
        for tip in tips:
            logger.info(tip)

# Global restart handler instance
restart_handler = RestartHandler()

def setup_restart_prevention():
    """Setup restart prevention measures"""
    restart_handler.setup_signal_handlers()
    restart_handler.log_system_info()
    restart_handler.create_restart_prevention_tips()

def check_service_health():
    """Check service health and log warnings"""
    return restart_handler.check_memory_usage()

# Environment variable helpers
def get_optimal_settings():
    """Get optimal settings for the current environment"""
    settings = {}
    
    # Detect if running on free tier (limited memory)
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        
        if total_gb < 1:  # Less than 1GB = likely free tier
            logger.info("🔍 Detected limited memory environment")
            settings.update({
                "WHISPER_MODEL": "tiny",
                "MAX_FILE_SIZE": 50 * 1024 * 1024,  # 50MB
                "MODEL_PRELOAD": "true",
                "DEBUG": "false"
            })
        else:
            logger.info("🔍 Detected standard memory environment")
            settings.update({
                "WHISPER_MODEL": "base",
                "MAX_FILE_SIZE": 100 * 1024 * 1024,  # 100MB
                "MODEL_PRELOAD": "true"
            })
            
    except Exception:
        # Fallback to conservative settings
        settings.update({
            "WHISPER_MODEL": "tiny",
            "MAX_FILE_SIZE": 50 * 1024 * 1024,
            "MODEL_PRELOAD": "true"
        })
    
    return settings

def apply_optimal_settings():
    """Apply optimal settings if not already set"""
    optimal = get_optimal_settings()
    applied = []
    
    for key, value in optimal.items():
        if not os.getenv(key):
            os.environ[key] = str(value)
            applied.append(f"{key}={value}")
    
    if applied:
        logger.info("⚙️ Applied optimal settings:")
        for setting in applied:
            logger.info(f"   {setting}")

if __name__ == "__main__":
    # Test the restart handler
    logging.basicConfig(level=logging.INFO)
    
    setup_restart_prevention()
    apply_optimal_settings()
    
    logger.info("✅ Restart handler test completed")
