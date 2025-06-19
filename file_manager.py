import os
import time
import threading
from typing import Dict, Optional
from utils import safe_delete_file, generate_unique_id, setup_logging

logger = setup_logging()

class FileManager:
    """
    Memory-efficient file manager with automatic cleanup
    Maintains ID-to-path mapping in memory with minimal overhead
    """
    
    def __init__(self, cleanup_interval=300, max_file_age=3600):
        self._file_map: Dict[str, dict] = {}  # ID -> {path, timestamp, type}
        self._lock = threading.Lock()
        self.cleanup_interval = cleanup_interval
        self.max_file_age = max_file_age
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        
        # Start background cleanup
        self._start_cleanup_thread()
    
    def register_file(self, file_path: str, file_type: str = 'audio') -> str:
        """
        Register a file and return unique ID
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('video' or 'audio')
            
        Returns:
            Unique ID for the file
        """
        file_id = generate_unique_id()
        
        with self._lock:
            self._file_map[file_id] = {
                'path': file_path,
                'timestamp': time.time(),
                'type': file_type
            }
        
        logger.info(f"Registered {file_type} file: {file_id} -> {file_path}")
        return file_id
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """
        Get file path by ID
        
        Args:
            file_id: Unique file ID
            
        Returns:
            File path if exists, None otherwise
        """
        with self._lock:
            file_info = self._file_map.get(file_id)
            if file_info and os.path.exists(file_info['path']):
                return file_info['path']
            elif file_info:
                # File doesn't exist, remove from map
                del self._file_map[file_id]
                logger.warning(f"File not found, removed from map: {file_id}")
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file and remove from map
        
        Args:
            file_id: Unique file ID
            
        Returns:
            True if successfully deleted, False otherwise
        """
        with self._lock:
            file_info = self._file_map.get(file_id)
            if not file_info:
                logger.warning(f"File ID not found in map: {file_id}")
                return False
            
            file_path = file_info['path']
            success = safe_delete_file(file_path)
            
            # Remove from map regardless of deletion success
            del self._file_map[file_id]
            logger.info(f"Removed from map: {file_id}")
            
            return success
    
    def get_stats(self) -> dict:
        """Get current file manager statistics"""
        with self._lock:
            total_files = len(self._file_map)
            audio_files = sum(1 for info in self._file_map.values() if info['type'] == 'audio')
            video_files = sum(1 for info in self._file_map.values() if info['type'] == 'video')
            
            return {
                'total_files': total_files,
                'audio_files': audio_files,
                'video_files': video_files,
                'memory_entries': total_files
            }
    
    def cleanup_expired_files(self):
        """Clean up expired files based on age"""
        current_time = time.time()
        expired_ids = []
        
        with self._lock:
            for file_id, file_info in self._file_map.items():
                if current_time - file_info['timestamp'] > self.max_file_age:
                    expired_ids.append(file_id)
        
        # Delete expired files
        for file_id in expired_ids:
            self.delete_file(file_id)
            logger.info(f"Cleaned up expired file: {file_id}")
        
        return len(expired_ids)
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while not self._stop_cleanup.wait(self.cleanup_interval):
                try:
                    cleaned = self.cleanup_expired_files()
                    if cleaned > 0:
                        logger.info(f"Background cleanup removed {cleaned} expired files")
                except Exception as e:
                    logger.error(f"Error in background cleanup: {str(e)}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.info("Started background cleanup thread")
    
    def shutdown(self):
        """Shutdown file manager and cleanup thread"""
        self._stop_cleanup.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        
        # Clean up all remaining files
        with self._lock:
            file_ids = list(self._file_map.keys())
        
        for file_id in file_ids:
            self.delete_file(file_id)
        
        logger.info("File manager shutdown complete")

# Global file manager instance
file_manager = FileManager()
