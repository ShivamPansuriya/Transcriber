# Video Transcription Service

A free, production-ready video transcription service built with FastAPI and OpenAI Whisper. Designed for deployment on Render.com's free tier with no transcription limits.

## Features

- 🎥 **Multiple Video Formats**: Supports MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V
- 🗣️ **Free Speech-to-Text**: Uses OpenAI Whisper (completely free, no API limits)
- 🌐 **REST API**: Simple endpoints for uploading and retrieving transcriptions
- ⚡ **Async Processing**: Non-blocking transcription for better performance
- 🛡️ **Rate Limiting**: Built-in protection against abuse
- 🧹 **Auto Cleanup**: Automatic removal of old transcriptions (3.5 hours)
- 📝 **Auto Documentation**: Interactive API docs at `/docs`
- 🚀 **Render Ready**: Optimized for Render.com free tier deployment

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd transcriber
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install FFmpeg**
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

3. **Run the Service**
   ```bash
   # Robust startup (recommended - prevents restarts)
   python start_robust.py

   # Or standard startup
   python main.py
   ```

4. **Access the API**
   - Service: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Logging and Monitoring

The service provides comprehensive step-by-step logging to track transcription progress:

**Enable Debug Logging:**
```bash
DEBUG=true python main.py
```

**Enable File Logging:**
```bash
LOG_TO_FILE=true python main.py
```

**Sample Log Output:**
```
2024-01-15 10:30:00 - main - INFO - 🚀 Starting transcription request for file: video.mp4
2024-01-15 10:30:00 - main - INFO - 🌐 Language specified: auto-detect
2024-01-15 10:30:00 - main - INFO - 📁 Validating file: video.mp4
2024-01-15 10:30:00 - main - INFO - 🔍 File extension: .mp4
2024-01-15 10:30:00 - main - INFO - ✅ File format validation passed: .mp4
2024-01-15 10:30:00 - main - INFO - 📊 Reading file content for size validation...
2024-01-15 10:30:00 - main - INFO - 📏 File size: 25.3MB (max: 100MB)
2024-01-15 10:30:00 - main - INFO - ✅ File size validation passed: 25.3MB
2024-01-15 10:30:00 - storage - INFO - 📝 Creating new transcription entry with ID: 1
2024-01-15 10:30:00 - transcription_service - INFO - 🎬 Starting video transcription for ID: 1
2024-01-15 10:30:00 - transcription_service - INFO - 🤖 Loading Whisper model: base
2024-01-15 10:30:15 - transcription_service - INFO - ✅ Whisper model loaded successfully in 15.2 seconds
2024-01-15 10:30:15 - transcription_service - INFO - 🎵 Extracting audio from video for transcription 1
2024-01-15 10:30:18 - transcription_service - INFO - ✅ Audio extraction completed in 3.1 seconds
2024-01-15 10:30:18 - transcription_service - INFO - 🗣️ Starting audio transcription for ID 1
2024-01-15 10:30:45 - transcription_service - INFO - ✅ Transcription completed in 27.3 seconds
2024-01-15 10:30:45 - transcription_service - INFO - 📝 Transcribed text length: 1247 characters
2024-01-15 10:30:45 - transcription_service - INFO - 🌐 Detected language: en
2024-01-15 10:30:45 - transcription_service - INFO - 🎉 Transcription 1 completed successfully in 45.6 seconds total
```

### Deploy to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Deploy"

3. **Configuration**
   - The service will automatically use the free tier
   - No environment variables needed (all configured automatically)
   - Health checks are configured at `/health`

## API Documentation

### Base URL
- Local: `http://localhost:8000`
- Render: `https://your-service-name.onrender.com`

### Endpoints

#### 1. Upload Video for Transcription

**POST** `/transcribe`

Upload a video file and get a transcription ID.

**Request:**
- **Content-Type**: `multipart/form-data`
- **file**: Video file (required) - Max 100MB
- **language**: Language code (optional) - e.g., 'en', 'es', 'fr'

**Response:**
```json
{
  "id": 123,
  "status": "pending",
  "message": "Transcription started. Use the ID to check status.",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@video.mp4" \
  -F "language=en"
```

**Example using Python:**
```python
import requests

with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/transcribe',
        files={'file': f},
        data={'language': 'en'}  # optional
    )
    
result = response.json()
transcription_id = result['id']
```

#### 2. Get Transcription Status/Results

**GET** `/transcribe/{id}`

Check transcription status and retrieve results.

**Response:**
```json
{
  "id": 123,
  "status": "completed",
  "text": "Hello, this is the transcribed text from your video...",
  "language": "en",
  "duration": 45.6,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z",
  "error_message": null
}
```

**Status Values:**
- `pending`: Transcription queued
- `processing`: Currently transcribing
- `completed`: Transcription finished successfully
- `failed`: Transcription failed (check error_message)

**Example:**
```bash
curl "http://localhost:8000/transcribe/123"
```

#### 3. Health Check

**GET** `/health`

Check service health and get statistics.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 5,
  "active_transcriptions": 2
}
```

### Error Handling

All errors return a consistent format:
```json
{
  "id": 0,
  "error": "error_type",
  "message": "Human readable error message"
}
```

**Common Error Codes:**
- `400`: Bad request (invalid file, unsupported format)
- `413`: File too large (>100MB)
- `404`: Transcription not found or expired
- `429`: Rate limit exceeded (>10 requests/minute)
- `500`: Internal server error

## Supported Languages

Whisper supports 99+ languages including:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)

Leave `language` empty for automatic detection.

## Limitations

### Free Tier Constraints
- **File Size**: 100MB maximum per video
- **Rate Limiting**: 10 requests per minute per IP
- **Storage**: Results stored for 3.5 hours only
- **Processing**: Sequential processing (one video at a time)
- **Cold Starts**: First request may take 30-60 seconds

### Technical Limitations
- **Video Length**: Longer videos take more time to process
- **Memory**: Large videos may fail on free tier (512MB RAM limit)
- **CPU**: Processing speed limited by free tier CPU allocation

## Troubleshooting

### Common Issues

1. **Service Restarts/Memory Issues**
   ```
   Process killed (signal 9) or frequent restarts
   ```
   **Solution:**
   ```bash
   # Use robust startup (automatically optimizes settings)
   python start_robust.py

   # Or manually use tiny model
   WHISPER_MODEL=tiny MODEL_PRELOAD=true python main.py
   ```
   **See:** [RESTART_TROUBLESHOOTING.md](RESTART_TROUBLESHOOTING.md)

2. **NumPy Compatibility Error**
   ```
   A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6
   ```
   **Solution:**
   ```bash
   python fix_numpy.py
   ```
   Or manually:
   ```bash
   pip uninstall numpy
   pip install 'numpy<2.0.0'
   pip install --force-reinstall torch torchaudio openai-whisper
   ```

2. **"File too large" Error**
   - Compress your video or use a shorter clip
   - Maximum file size is 100MB

3. **"Unsupported file format" Error**
   - Convert to supported format: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V

4. **Slow Processing**
   - First request loads the AI model (30-60 seconds)
   - Subsequent requests are faster
   - Longer videos take more time

5. **"Transcription not found" Error**
   - Transcriptions expire after 3.5 hours
   - Check if the ID is correct

6. **Rate Limit Exceeded**
   - Wait 1 minute before making more requests
   - Maximum 10 requests per minute per IP

### Render.com Specific

1. **Service Sleeping**
   - Free tier services sleep after 15 minutes of inactivity
   - First request after sleep takes 30-60 seconds

2. **Build Failures**
   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt

3. **Memory Issues**
   - Free tier has 512MB RAM limit
   - Large videos may cause out-of-memory errors

## Development

### Project Structure
```
transcriber/
├── main.py                 # FastAPI application
├── transcription_service.py # Core transcription logic
├── storage.py              # In-memory storage manager
├── models.py               # Pydantic data models
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── render.yaml             # Render deployment config
└── README.md               # This file
```

### Adding Features

1. **New Video Formats**: Add to `ALLOWED_EXTENSIONS` in `config.py`
2. **Different Models**: Change `WHISPER_MODEL` in `config.py`
3. **Longer Storage**: Modify `CLEANUP_INTERVAL_HOURS` in `config.py`
4. **Rate Limits**: Adjust `RATE_LIMIT_REQUESTS` in `config.py`

### Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (create test files as needed)
pytest
```

## License

MIT License - feel free to use for any purpose.

## Support

- 📖 **Documentation**: Visit `/docs` endpoint for interactive API docs
- 🐛 **Issues**: Report bugs via GitHub issues
- 💡 **Features**: Suggest improvements via GitHub discussions

---

**Ready to transcribe? Upload your first video at `/docs` or use the API endpoints above!**
