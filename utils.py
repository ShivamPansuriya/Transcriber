import logging
import os
import time
import uuid
from functools import wraps
from flask import jsonify

def setup_logging(log_level='INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def generate_unique_id():
    """Generate a unique ID for file tracking"""
    return str(uuid.uuid4())

def safe_delete_file(file_path):
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Successfully deleted file: {file_path}")
            return True
        else:
            logging.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {str(e)}")
        return False

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def cleanup_old_files(directory, max_age_seconds=3600):
    """Clean up old files in directory"""
    current_time = time.time()
    cleaned_count = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > max_age_seconds:
                    if safe_delete_file(file_path):
                        cleaned_count += 1
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")
    
    if cleaned_count > 0:
        logging.info(f"Cleaned up {cleaned_count} old files")
    
    return cleaned_count

def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
    return decorated_function

def log_memory_usage():
    """Log current memory usage (basic implementation)"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        logging.info(f"Current memory usage: {memory_mb:.2f} MB")
        return memory_mb
    except ImportError:
        # psutil not available, skip memory logging
        return None
    except Exception as e:
        logging.warning(f"Could not get memory usage: {str(e)}")
        return None
