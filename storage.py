import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from models import TranscriptionResult, TranscriptionStatus
from config import settings
import logging

logger = logging.getLogger(__name__)

class InMemoryStorage:
    def __init__(self):
        self._storage: Dict[int, TranscriptionResult] = {}
        self._next_id = 1
        self._cleanup_task = None
        
    async def start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
    async def stop_cleanup_task(self):
        """Stop the background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    def create_transcription(self, language: Optional[str] = None) -> int:
        """Create a new transcription entry and return its ID"""
        transcription_id = self._next_id
        self._next_id += 1
        
        result = TranscriptionResult(
            id=transcription_id,
            status=TranscriptionStatus.PENDING,
            language=language,
            created_at=datetime.utcnow()
        )
        
        self._storage[transcription_id] = result
        logger.info(f"Created transcription {transcription_id}")
        return transcription_id
    
    def get_transcription(self, transcription_id: int) -> Optional[TranscriptionResult]:
        """Get transcription by ID"""
        return self._storage.get(transcription_id)
    
    def update_transcription(self, transcription_id: int, **kwargs) -> bool:
        """Update transcription fields"""
        if transcription_id not in self._storage:
            return False
            
        result = self._storage[transcription_id]
        for key, value in kwargs.items():
            if hasattr(result, key):
                setattr(result, key, value)
        
        logger.info(f"Updated transcription {transcription_id}: {kwargs}")
        return True
    
    def delete_transcription(self, transcription_id: int) -> bool:
        """Delete transcription by ID"""
        if transcription_id in self._storage:
            del self._storage[transcription_id]
            logger.info(f"Deleted transcription {transcription_id}")
            return True
        return False
    
    async def _cleanup_loop(self):
        """Background task to clean up old transcriptions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                await self._cleanup_old_transcriptions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_transcriptions(self):
        """Remove transcriptions older than the configured time"""
        cutoff_time = datetime.utcnow() - timedelta(hours=settings.CLEANUP_INTERVAL_HOURS)
        to_delete = []
        
        for transcription_id, result in self._storage.items():
            if result.created_at < cutoff_time:
                to_delete.append(transcription_id)
        
        for transcription_id in to_delete:
            self.delete_transcription(transcription_id)
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old transcriptions")

# Global storage instance
storage = InMemoryStorage()
