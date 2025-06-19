import os
import tempfile

class Config:
    """Base configuration class"""
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # File handling settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = tempfile.gettempdir()
    ALLOWED_VIDEO_EXTENSIONS = {
        'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'
    }
    
    # Audio extraction settings
    AUDIO_FORMAT = 'mp3'
    AUDIO_BITRATE = '128k'  # Optimize for size while maintaining quality
    
    # Memory management
    CLEANUP_INTERVAL = 300  # 5 minutes cleanup interval for orphaned files
    MAX_FILE_AGE = 3600     # 1 hour max age for temporary files
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def is_allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_VIDEO_EXTENSIONS

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = False  # Disable debug mode to avoid watchdog issues
    LOG_LEVEL = 'INFO'

class ProductionConfig(Config):
    """Production configuration for Render.com"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    # Render.com provides PORT via environment variable
    PORT = int(os.getenv('PORT', 10000))

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
