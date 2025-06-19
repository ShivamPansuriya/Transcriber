import os
import tempfile
import ffmpeg
from typing import Tuple, Optional
from config import Config
from utils import safe_delete_file, get_file_size_mb, setup_logging

logger = setup_logging()

class AudioProcessor:
    """
    Efficient audio extraction from video files
    Optimized for memory-constrained environments
    """
    
    def __init__(self):
        self.config = Config()
    
    def extract_audio(self, video_path: str, delete_video: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to input video file
            delete_video: Whether to delete video file after extraction
            
        Returns:
            Tuple of (audio_file_path, error_message)
            Returns (None, error_message) if extraction fails
        """
        if not os.path.exists(video_path):
            return None, f"Video file not found: {video_path}"
        
        # Log input file info
        video_size_mb = get_file_size_mb(video_path)
        logger.info(f"Processing video file: {video_path} ({video_size_mb:.2f} MB)")
        
        # Generate output audio file path
        audio_path = self._generate_audio_path(video_path)
        
        try:
            # Extract audio using ffmpeg
            success, error = self._run_ffmpeg_extraction(video_path, audio_path)
            
            if not success:
                # Clean up partial audio file if exists
                safe_delete_file(audio_path)
                return None, error
            
            # Verify audio file was created
            if not os.path.exists(audio_path):
                return None, "Audio extraction completed but output file not found"
            
            # Log output file info
            audio_size_mb = get_file_size_mb(audio_path)
            logger.info(f"Audio extracted successfully: {audio_path} ({audio_size_mb:.2f} MB)")
            
            # Delete video file immediately after successful extraction
            if delete_video:
                if safe_delete_file(video_path):
                    logger.info(f"Video file deleted after extraction: {video_path}")
                else:
                    logger.warning(f"Failed to delete video file: {video_path}")
            
            return audio_path, None
            
        except Exception as e:
            error_msg = f"Audio extraction failed: {str(e)}"
            logger.error(error_msg)
            
            # Clean up any partial files
            safe_delete_file(audio_path)
            if delete_video:
                safe_delete_file(video_path)
            
            return None, error_msg
    
    def _generate_audio_path(self, video_path: str) -> str:
        """Generate output audio file path"""
        # Create temporary file with proper extension
        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_filename = f"{base_name}_{int(os.urandom(4).hex(), 16)}.{self.config.AUDIO_FORMAT}"
        return os.path.join(temp_dir, audio_filename)
    
    def _run_ffmpeg_extraction(self, video_path: str, audio_path: str) -> Tuple[bool, Optional[str]]:
        """
        Run ffmpeg audio extraction
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Configure ffmpeg stream
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec='mp3',  # Use MP3 codec for broad compatibility
                audio_bitrate=self.config.AUDIO_BITRATE,
                ac=2,  # Stereo
                ar=44100,  # Sample rate
                map_metadata=-1,  # Remove metadata to reduce file size
                y=None  # Overwrite output file if exists
            )

            # Run ffmpeg with error capture
            out, err = ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

            logger.info("FFmpeg extraction completed successfully")
            return True, None

        except ffmpeg.Error as e:
            # Handle FFmpeg errors properly
            stderr_output = e.stderr.decode('utf-8') if e.stderr else 'No error details available'
            error_msg = f"FFmpeg error: {stderr_output}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error during FFmpeg execution: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get basic video information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video info or None if error
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            info = {
                'duration': float(probe['format'].get('duration', 0)),
                'size_mb': get_file_size_mb(video_path),
                'has_video': video_stream is not None,
                'has_audio': audio_stream is not None
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'video_codec': video_stream.get('codec_name', 'unknown')
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', 'unknown'),
                    'sample_rate': int(audio_stream.get('sample_rate', 0))
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None

# Global audio processor instance
audio_processor = AudioProcessor()
