import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from models import TranscriptionResult, TranscriptionStatus
from config import settings
import logging

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InMemoryStorage:
    def __init__(self):
        self._storage: Dict[int, TranscriptionResult] = {}
        self._next_id = 1
        self._cleanup_task = None
        
    async def start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._cleanup_task is None:
            logger.info("🧹 Starting automatic cleanup task")
            logger.info(f"⏰ Cleanup interval: {settings.CLEANUP_INTERVAL_HOURS} hours")
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        else:
            logger.info("🧹 Cleanup task already running")

    async def stop_cleanup_task(self):
        """Stop the background cleanup task"""
        if self._cleanup_task:
            logger.info("🛑 Stopping cleanup task")
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("✅ Cleanup task stopped")
        else:
            logger.info("🧹 No cleanup task to stop")
    
    def create_transcription(self, language: Optional[str] = None) -> int:
        """Create a new transcription entry and return its ID"""
        transcription_id = self._next_id
        self._next_id += 1

        logger.info(f"📝 Creating new transcription entry with ID: {transcription_id}")
        logger.info(f"🌐 Language: {language or 'auto-detect'}")

        result = TranscriptionResult(
            id=transcription_id,
            status=TranscriptionStatus.PENDING,
            language=language,
            created_at=datetime.now(timezone.utc)
        )

        self._storage[transcription_id] = result
        logger.info(f"✅ Transcription {transcription_id} created successfully")
        logger.info(f"📊 Total active transcriptions: {len(self._storage)}")
        return transcription_id
    
    def get_transcription(self, transcription_id: int) -> Optional[TranscriptionResult]:
        """Get transcription by ID"""
        logger.info(f"🔍 Looking up transcription ID: {transcription_id}")
        result = self._storage.get(transcription_id)
        if result:
            logger.info(f"✅ Found transcription {transcription_id} with status: {result.status}")
        else:
            logger.warning(f"❌ Transcription {transcription_id} not found")
        return result

    def update_transcription(self, transcription_id: int, **kwargs) -> bool:
        """Update transcription fields"""
        if transcription_id not in self._storage:
            logger.warning(f"❌ Cannot update transcription {transcription_id} - not found")
            return False

        result = self._storage[transcription_id]
        old_status = result.status if hasattr(result, 'status') else 'unknown'

        for key, value in kwargs.items():
            if hasattr(result, key):
                setattr(result, key, value)

        new_status = result.status if hasattr(result, 'status') else 'unknown'
        logger.info(f"📝 Updated transcription {transcription_id}")

        if 'status' in kwargs:
            logger.info(f"🔄 Status changed: {old_status} → {new_status}")

        # Log specific updates
        for key, value in kwargs.items():
            if key == 'text' and value:
                text_preview = value[:50] + "..." if len(value) > 50 else value
                logger.info(f"📄 Text updated: {text_preview}")
            elif key == 'error_message' and value:
                logger.error(f"❌ Error recorded: {value}")
            elif key not in ['status', 'text', 'error_message']:
                logger.info(f"📊 {key}: {value}")

        return True

    def delete_transcription(self, transcription_id: int) -> bool:
        """Delete transcription by ID"""
        if transcription_id in self._storage:
            result = self._storage[transcription_id]
            del self._storage[transcription_id]
            logger.info(f"🗑️ Deleted transcription {transcription_id} (status: {result.status})")
            logger.info(f"📊 Remaining transcriptions: {len(self._storage)}")
            return True
        else:
            logger.warning(f"❌ Cannot delete transcription {transcription_id} - not found")
            return False
    
    async def _cleanup_loop(self):
        """Background task to clean up old transcriptions"""
        logger.info("🧹 Cleanup loop started")
        while True:
            try:
                logger.info("😴 Cleanup sleeping for 1 hour...")
                await asyncio.sleep(3600)  # Check every hour
                logger.info("⏰ Running scheduled cleanup...")
                await self._cleanup_old_transcriptions()
            except asyncio.CancelledError:
                logger.info("🛑 Cleanup loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")

    async def _cleanup_old_transcriptions(self):
        """Remove transcriptions older than the configured time"""
        logger.info("🧹 Starting cleanup of old transcriptions...")
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=settings.CLEANUP_INTERVAL_HOURS)
        logger.info(f"⏰ Cutoff time: {cutoff_time} (older than {settings.CLEANUP_INTERVAL_HOURS} hours)")

        to_delete = []

        for transcription_id, result in self._storage.items():
            age_hours = (datetime.now(timezone.utc) - result.created_at).total_seconds() / 3600
            if result.created_at < cutoff_time:
                logger.info(f"🗑️ Marking transcription {transcription_id} for deletion (age: {age_hours:.1f} hours)")
                to_delete.append(transcription_id)

        if not to_delete:
            logger.info("✅ No old transcriptions to clean up")
            return

        logger.info(f"🧹 Deleting {len(to_delete)} old transcriptions...")
        for transcription_id in to_delete:
            self.delete_transcription(transcription_id)

        logger.info(f"✅ Cleanup completed - removed {len(to_delete)} transcriptions")
        logger.info(f"📊 Active transcriptions remaining: {len(self._storage)}")

# Global storage instance
storage = InMemoryStorage()
