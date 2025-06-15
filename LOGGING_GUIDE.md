# Comprehensive Logging Guide

The Video Transcription Service now includes detailed step-by-step logging to help you monitor and debug transcription progress.

## 🎯 **What You Can Track**

### Complete Transcription Journey
- ✅ File upload and validation
- ✅ Video processing steps
- ✅ Whisper model loading
- ✅ Audio extraction progress
- ✅ Transcription inference
- ✅ Results and cleanup
- ✅ Error handling and debugging

### Real-time Progress Monitoring
- 📊 Processing times for each step
- 📏 File sizes and durations
- 🌐 Language detection
- 📝 Text length and previews
- ⚠️ Warnings and errors

## 🚀 **Quick Start**

### Basic Logging (Default)
```bash
python main.py
```

### Debug Mode (Detailed Logs)
```bash
DEBUG=true python main.py
```

### Log to File
```bash
LOG_TO_FILE=true python main.py
```

### Combined (Debug + File)
```bash
DEBUG=true LOG_TO_FILE=true python main.py
```

## 📊 **Real-time Monitoring**

### Monitor Service Health
```bash
python log_monitor.py test
```

### Upload and Monitor Video
```bash
python log_monitor.py upload video.mp4
```

### Monitor Existing Transcription
```bash
python log_monitor.py monitor 123
```

## 📋 **Sample Log Output**

### Service Startup
```
2024-01-15 10:30:00 - main - INFO - 🚀 Starting Video Transcription Service
2024-01-15 10:30:00 - main - INFO - ==================================================
2024-01-15 10:30:00 - main - INFO - 📋 Service Configuration:
2024-01-15 10:30:00 - main - INFO -    🤖 Whisper Model: base
2024-01-15 10:30:00 - main - INFO -    📏 Max File Size: 100MB
2024-01-15 10:30:00 - main - INFO -    🕒 Cleanup Interval: 3.5 hours
2024-01-15 10:30:00 - main - INFO -    🚦 Rate Limit: 10 requests/minute
2024-01-15 10:30:00 - main - INFO -    🌐 Host: 0.0.0.0:8000
2024-01-15 10:30:00 - main - INFO -    📁 Supported Formats: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v
2024-01-15 10:30:00 - main - INFO - ==================================================
```

### File Upload Process
```
2024-01-15 10:30:15 - main - INFO - 🚀 Starting transcription request for file: video.mp4
2024-01-15 10:30:15 - main - INFO - 🌐 Language specified: auto-detect
2024-01-15 10:30:15 - main - INFO - 📁 Validating file: video.mp4
2024-01-15 10:30:15 - main - INFO - 🔍 File extension: .mp4
2024-01-15 10:30:15 - main - INFO - ✅ File format validation passed: .mp4
2024-01-15 10:30:15 - main - INFO - 📊 Reading file content for size validation...
2024-01-15 10:30:15 - main - INFO - 📏 File size: 25.34MB (max: 100MB)
2024-01-15 10:30:15 - main - INFO - ✅ File size validation passed: 25.34MB
```

### Storage Operations
```
2024-01-15 10:30:15 - storage - INFO - 📝 Creating new transcription entry with ID: 1
2024-01-15 10:30:15 - storage - INFO - 🌐 Language: auto-detect
2024-01-15 10:30:15 - storage - INFO - ✅ Transcription 1 created successfully
2024-01-15 10:30:15 - storage - INFO - 📊 Total active transcriptions: 1
```

### Video Processing
```
2024-01-15 10:30:15 - transcription_service - INFO - 🎬 Starting video transcription for ID: 1
2024-01-15 10:30:15 - transcription_service - INFO - 📊 Video size: 25.34MB
2024-01-15 10:30:15 - transcription_service - INFO - 🌐 Language: auto-detect
2024-01-15 10:30:15 - transcription_service - INFO - 📝 Updating status to PROCESSING for ID: 1
```

### Model Loading (First Time)
```
2024-01-15 10:30:15 - transcription_service - INFO - 🤖 Loading Whisper model: base
2024-01-15 10:30:15 - transcription_service - INFO - 📥 This may take 30-60 seconds for first-time download...
2024-01-15 10:30:45 - transcription_service - INFO - ✅ Whisper model loaded successfully in 30.2 seconds
```

### Audio Extraction
```
2024-01-15 10:30:45 - transcription_service - INFO - 🎵 Extracting audio from video for transcription 1
2024-01-15 10:30:45 - transcription_service - INFO - 📁 Creating temporary video file...
2024-01-15 10:30:45 - transcription_service - INFO - 📁 Temporary files created - Video: /tmp/xyz.tmp, Audio: /tmp/abc.wav
2024-01-15 10:30:45 - transcription_service - INFO - 🎵 Running FFmpeg to extract audio...
2024-01-15 10:30:45 - transcription_service - INFO - 🔧 Configuring FFmpeg for audio extraction...
2024-01-15 10:30:45 - transcription_service - INFO -    - Codec: PCM 16-bit
2024-01-15 10:30:45 - transcription_service - INFO -    - Channels: 1 (mono)
2024-01-15 10:30:45 - transcription_service - INFO -    - Sample rate: 16kHz
2024-01-15 10:30:48 - transcription_service - INFO - ✅ FFmpeg audio extraction completed
2024-01-15 10:30:48 - transcription_service - INFO - ✅ Audio extraction successful - Size: 8.45MB
2024-01-15 10:30:48 - transcription_service - INFO - ✅ Audio extraction completed in 3.1 seconds
```

### Transcription Process
```
2024-01-15 10:30:48 - transcription_service - INFO - 🗣️ Starting audio transcription for ID 1
2024-01-15 10:30:48 - transcription_service - INFO - 🗣️ Starting Whisper transcription...
2024-01-15 10:30:48 - transcription_service - INFO - 🎵 Audio file: /tmp/abc.wav
2024-01-15 10:30:48 - transcription_service - INFO - 🌐 Language: auto-detect
2024-01-15 10:30:48 - transcription_service - INFO - ⚡ Running transcription in background thread...
2024-01-15 10:30:48 - transcription_service - INFO - 🤖 Preparing Whisper transcription options...
2024-01-15 10:30:48 - transcription_service - INFO - 🌐 Language: auto-detect
2024-01-15 10:30:48 - transcription_service - INFO - 🎯 Starting Whisper model inference...
2024-01-15 10:31:15 - transcription_service - INFO - ✅ Whisper inference completed in 27.3 seconds
2024-01-15 10:31:15 - transcription_service - INFO - 📝 Text length: 1247 characters
2024-01-15 10:31:15 - transcription_service - INFO - 🌐 Detected language: en
2024-01-15 10:31:15 - transcription_service - INFO - ⏱️ Audio duration: 180.50 seconds
2024-01-15 10:31:15 - transcription_service - INFO - 📄 Text preview: Hello, welcome to this video tutorial where we'll be discussing...
```

### Completion
```
2024-01-15 10:31:15 - transcription_service - INFO - ✅ Transcription completed in 27.3 seconds
2024-01-15 10:31:15 - transcription_service - INFO - 💾 Saving transcription results for ID 1
2024-01-15 10:31:15 - storage - INFO - 📝 Updated transcription 1
2024-01-15 10:31:15 - storage - INFO - 🔄 Status changed: processing → completed
2024-01-15 10:31:15 - storage - INFO - 📄 Text updated: Hello, welcome to this video tutorial where we'll...
2024-01-15 10:31:15 - transcription_service - INFO - 🧹 Cleaning up temporary audio file
2024-01-15 10:31:15 - transcription_service - INFO - 🎉 Transcription 1 completed successfully in 60.2 seconds total
```

## 🔧 **Log Levels**

### INFO (Default)
- Service startup/shutdown
- Request processing
- Status updates
- Completion messages

### DEBUG (Detailed)
- File validation details
- Temporary file paths
- FFmpeg configuration
- Model loading progress
- Memory usage info

### WARNING
- Large file warnings
- Performance issues
- Non-critical errors

### ERROR
- Processing failures
- File format issues
- System errors
- Transcription failures

## 📁 **Log Files**

When `LOG_TO_FILE=true`, logs are saved to:
```
transcription_service_YYYYMMDD_HHMMSS.log
```

Example: `transcription_service_20240115_103000.log`

## 🛠️ **Troubleshooting with Logs**

### Common Issues and Log Patterns

**1. NumPy Compatibility Error**
```
ERROR - A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6
```
**Solution:** Run `python fix_numpy.py`

**2. FFmpeg Not Found**
```
ERROR - FFmpeg audio extraction failed: [Errno 2] No such file or directory: 'ffmpeg'
```
**Solution:** Install FFmpeg for your OS

**3. File Too Large**
```
ERROR - File too large: 150.5MB > 100MB
```
**Solution:** Compress video or increase limit in config.py

**4. Model Loading Issues**
```
ERROR - Failed to load Whisper model: [Errno 28] No space left on device
```
**Solution:** Free up disk space or use smaller model

**5. Memory Issues**
```
ERROR - Process killed (signal 9)
```
**Solution:** Use smaller files or increase available memory

## 🎯 **Performance Monitoring**

### Key Metrics to Watch
- **Model Loading Time**: Should be 15-60 seconds (first time only)
- **Audio Extraction**: Usually 1-5 seconds per minute of video
- **Transcription Speed**: Varies by model and content (typically 0.1-0.5x real-time)
- **Memory Usage**: Monitor for large files
- **Active Transcriptions**: Track concurrent processing

### Optimization Tips
- Use `tiny` model for faster processing
- Compress videos before upload
- Monitor memory usage with large files
- Use DEBUG mode to identify bottlenecks

## 📊 **Integration Examples**

### Parse Logs Programmatically
```python
import re
from datetime import datetime

def parse_transcription_logs(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            if 'Transcription' in line and 'completed successfully' in line:
                # Extract transcription ID and time
                match = re.search(r'Transcription (\d+) completed.*in ([\d.]+) seconds', line)
                if match:
                    tid, duration = match.groups()
                    print(f"ID {tid}: {duration}s")
```

### Monitor API Programmatically
```python
import requests
import time

def monitor_service():
    while True:
        try:
            response = requests.get('http://localhost:8000/health')
            health = response.json()
            print(f"Active: {health.get('active_transcriptions', 0)}")
            time.sleep(30)
        except Exception as e:
            print(f"Service down: {e}")
            time.sleep(60)
```

---

**With comprehensive logging, you now have complete visibility into your transcription service! 🎉**
