import whisper
import ffmpeg
import tempfile
import os
import asyncio
import logging
import time
from typing import Optional
from datetime import datetime, timezone
from storage import storage
from models import TranscriptionStatus
from config import settings

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self):
        self._model = None
        self._model_loading = False
        self._model_load_error = None
    
    async def preload_model(self):
        """Preload Whisper model during startup to avoid request timeouts"""
        if self._model is not None:
            logger.info("🤖 Whisper model already loaded")
            return True

        if self._model_load_error:
            logger.error(f"❌ Previous model load failed: {self._model_load_error}")
            return False

        try:
            logger.info(f"🚀 Preloading Whisper model: {settings.WHISPER_MODEL}")
            logger.info("📥 This may take 30-60 seconds for first-time download...")
            logger.info("⚡ Preloading during startup to avoid request timeouts...")

            start_time = time.time()

            # Run in thread pool to avoid blocking startup
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                whisper.load_model,
                settings.WHISPER_MODEL
            )

            load_time = time.time() - start_time
            logger.info(f"✅ Whisper model preloaded successfully in {load_time:.2f} seconds")
            logger.info("🎯 Service ready for transcription requests!")
            return True

        except Exception as e:
            error_msg = f"Failed to preload Whisper model: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self._model_load_error = error_msg
            return False

    async def _load_model(self):
        """Load Whisper model asynchronously (fallback if not preloaded)"""
        if self._model is not None:
            logger.info("🤖 Whisper model already loaded")
            return

        if self._model_load_error:
            logger.error(f"❌ Model load error: {self._model_load_error}")
            raise Exception(self._model_load_error)

        if self._model_loading:
            logger.info("⏳ Whisper model is currently loading, waiting...")
            # Wait for model to load
            while self._model_loading:
                await asyncio.sleep(0.1)
            if self._model is None:
                raise Exception("Model loading failed")
            logger.info("✅ Whisper model loading completed (waited)")
            return

        # If we get here, model wasn't preloaded - try to load it now
        logger.warning("⚠️ Model not preloaded, loading during request (may cause timeout)")
        self._model_loading = True
        try:
            logger.info(f"🤖 Loading Whisper model: {settings.WHISPER_MODEL}")
            start_time = time.time()

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                whisper.load_model,
                settings.WHISPER_MODEL
            )

            load_time = time.time() - start_time
            logger.info(f"✅ Whisper model loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            error_msg = f"Failed to load Whisper model: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self._model_load_error = error_msg
            raise Exception(error_msg)
        finally:
            self._model_loading = False
    
    async def transcribe_video(self, video_content: bytes, transcription_id: int, language: Optional[str] = None):
        """Transcribe video content asynchronously"""
        start_time = time.time()
        logger.info(f"🎬 Starting video transcription for ID: {transcription_id}")
        logger.info(f"📊 Video size: {len(video_content) / (1024*1024):.2f}MB")
        logger.info(f"🌐 Language: {language or 'auto-detect'}")

        # Check memory before starting
        from restart_handler import check_service_health
        if check_service_health():
            logger.warning(f"⚠️ High memory usage detected before transcription {transcription_id}")

        try:
            # Update status to processing
            logger.info(f"📝 Updating status to PROCESSING for ID: {transcription_id}")
            storage.update_transcription(
                transcription_id,
                status=TranscriptionStatus.PROCESSING
            )

            # Load model if needed
            logger.info(f"🤖 Loading Whisper model for transcription {transcription_id}")
            await self._load_model()

            # Extract audio from video
            logger.info(f"🎵 Extracting audio from video for transcription {transcription_id}")
            audio_start = time.time()
            audio_path = await self._extract_audio(video_content)
            audio_time = time.time() - audio_start
            logger.info(f"✅ Audio extraction completed in {audio_time:.2f} seconds")

            try:
                # Transcribe audio
                logger.info(f"🗣️ Starting audio transcription for ID {transcription_id}")
                transcribe_start = time.time()
                result = await self._transcribe_audio(audio_path, language)
                transcribe_time = time.time() - transcribe_start

                # Log transcription results
                text_length = len(result["text"]) if result["text"] else 0
                logger.info(f"✅ Transcription completed in {transcribe_time:.2f} seconds")
                logger.info(f"📝 Transcribed text length: {text_length} characters")
                logger.info(f"🌐 Detected language: {result.get('language', 'unknown')}")
                logger.info(f"⏱️ Audio duration: {result.get('duration', 'unknown')} seconds")

                # Update storage with results
                logger.info(f"💾 Saving transcription results for ID {transcription_id}")
                storage.update_transcription(
                    transcription_id,
                    status=TranscriptionStatus.COMPLETED,
                    text=result["text"],
                    language=result["language"],
                    duration=result.get("duration"),
                    completed_at=datetime.now(timezone.utc)
                )

                total_time = time.time() - start_time
                logger.info(f"🎉 Transcription {transcription_id} completed successfully in {total_time:.2f} seconds total")

            finally:
                # Clean up audio file
                if os.path.exists(audio_path):
                    logger.info(f"🧹 Cleaning up temporary audio file")
                    os.unlink(audio_path)

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"❌ Transcription {transcription_id} failed after {total_time:.2f} seconds: {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            storage.update_transcription(
                transcription_id,
                status=TranscriptionStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _extract_audio(self, video_content: bytes) -> str:
        """Extract audio from video content"""
        logger.info("📁 Creating temporary video file...")

        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as video_file:
            video_file.write(video_content)
            video_path = video_file.name

        audio_path = tempfile.mktemp(suffix='.wav')
        logger.info(f"📁 Temporary files created - Video: {video_path}, Audio: {audio_path}")

        try:
            # Extract audio using ffmpeg
            logger.info("🎵 Running FFmpeg to extract audio...")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._extract_audio_sync,
                video_path,
                audio_path
            )

            # Check if audio file was created successfully
            if os.path.exists(audio_path):
                audio_size = os.path.getsize(audio_path)
                logger.info(f"✅ Audio extraction successful - Size: {audio_size / (1024*1024):.2f}MB")
            else:
                logger.error("❌ Audio file was not created")
                raise Exception("Audio extraction failed - no output file")

            return audio_path
        finally:
            # Clean up video file
            if os.path.exists(video_path):
                logger.info("🧹 Cleaning up temporary video file")
                os.unlink(video_path)
    
    def _extract_audio_sync(self, video_path: str, audio_path: str):
        """Synchronous audio extraction"""
        try:
            logger.info("🔧 Configuring FFmpeg for audio extraction...")
            logger.info("   - Codec: PCM 16-bit")
            logger.info("   - Channels: 1 (mono)")
            logger.info("   - Sample rate: 16kHz")

            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            logger.info("✅ FFmpeg audio extraction completed")
        except Exception as e:
            logger.error(f"❌ FFmpeg audio extraction failed: {str(e)}")
            raise
    
    async def _transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> dict:
        """Transcribe audio file"""
        logger.info(f"🗣️ Starting Whisper transcription...")
        logger.info(f"🎵 Audio file: {audio_path}")
        logger.info(f"🌐 Language: {language or 'auto-detect'}")

        loop = asyncio.get_event_loop()

        # Run transcription in thread pool
        logger.info("⚡ Running transcription in background thread...")
        result = await loop.run_in_executor(
            None,
            self._transcribe_audio_sync,
            audio_path,
            language
        )

        logger.info("✅ Whisper transcription completed")
        return result
    
    def _transcribe_audio_sync(self, audio_path: str, language: Optional[str] = None) -> dict:
        """Synchronous audio transcription"""
        try:
            logger.info("🤖 Preparing Whisper transcription options...")
            options = {}
            if language:
                options['language'] = language
                logger.info(f"🌐 Language specified: {language}")
            else:
                logger.info("🌐 Language: auto-detect")

            logger.info("🎯 Starting Whisper model inference...")
            start_time = time.time()
            result = self._model.transcribe(audio_path, **options)
            inference_time = time.time() - start_time

            # Log detailed results
            text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            duration = result.get("duration", 0)

            logger.info(f"✅ Whisper inference completed in {inference_time:.2f} seconds")
            logger.info(f"📝 Text length: {len(text)} characters")
            logger.info(f"🌐 Detected language: {detected_language}")
            logger.info(f"⏱️ Audio duration: {duration:.2f} seconds")

            if len(text) > 100:
                logger.info(f"📄 Text preview: {text[:100]}...")
            else:
                logger.info(f"📄 Full text: {text}")

            return {
                "text": text,
                "language": detected_language,
                "duration": duration
            }
        except Exception as e:
            logger.error(f"❌ Whisper transcription failed: {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            raise

# Global service instance
transcription_service = TranscriptionService()
