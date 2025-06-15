import whisper
import ffmpeg
import tempfile
import os
import asyncio
import logging
from typing import Optional, Tuple
from datetime import datetime
from storage import storage
from models import TranscriptionStatus
from config import settings

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self._model = None
        self._model_loading = False
    
    async def _load_model(self):
        """Load Whisper model asynchronously"""
        if self._model is not None:
            return
            
        if self._model_loading:
            # Wait for model to load
            while self._model_loading:
                await asyncio.sleep(0.1)
            return
            
        self._model_loading = True
        try:
            logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None, 
                whisper.load_model, 
                settings.WHISPER_MODEL
            )
            logger.info("Whisper model loaded successfully")
        finally:
            self._model_loading = False
    
    async def transcribe_video(self, video_content: bytes, transcription_id: int, language: Optional[str] = None):
        """Transcribe video content asynchronously"""
        try:
            # Update status to processing
            storage.update_transcription(
                transcription_id, 
                status=TranscriptionStatus.PROCESSING
            )
            
            # Load model if needed
            await self._load_model()
            
            # Extract audio from video
            logger.info(f"Extracting audio for transcription {transcription_id}")
            audio_path = await self._extract_audio(video_content)
            
            try:
                # Transcribe audio
                logger.info(f"Starting transcription {transcription_id}")
                result = await self._transcribe_audio(audio_path, language)
                
                # Update storage with results
                storage.update_transcription(
                    transcription_id,
                    status=TranscriptionStatus.COMPLETED,
                    text=result["text"],
                    language=result["language"],
                    duration=result.get("duration"),
                    completed_at=datetime.utcnow()
                )
                
                logger.info(f"Transcription {transcription_id} completed successfully")
                
            finally:
                # Clean up audio file
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                    
        except Exception as e:
            logger.error(f"Transcription {transcription_id} failed: {str(e)}")
            storage.update_transcription(
                transcription_id,
                status=TranscriptionStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.utcnow()
            )
    
    async def _extract_audio(self, video_content: bytes) -> str:
        """Extract audio from video content"""
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as video_file:
            video_file.write(video_content)
            video_path = video_file.name
        
        audio_path = tempfile.mktemp(suffix='.wav')
        
        try:
            # Extract audio using ffmpeg
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._extract_audio_sync,
                video_path,
                audio_path
            )
            return audio_path
        finally:
            # Clean up video file
            if os.path.exists(video_path):
                os.unlink(video_path)
    
    def _extract_audio_sync(self, video_path: str, audio_path: str):
        """Synchronous audio extraction"""
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )
    
    async def _transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> dict:
        """Transcribe audio file"""
        loop = asyncio.get_event_loop()
        
        # Run transcription in thread pool
        result = await loop.run_in_executor(
            None,
            self._transcribe_audio_sync,
            audio_path,
            language
        )
        
        return result
    
    def _transcribe_audio_sync(self, audio_path: str, language: Optional[str] = None) -> dict:
        """Synchronous audio transcription"""
        options = {}
        if language:
            options['language'] = language
            
        result = self._model.transcribe(audio_path, **options)
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language"),
            "duration": result.get("duration")
        }

# Global service instance
transcription_service = TranscriptionService()
