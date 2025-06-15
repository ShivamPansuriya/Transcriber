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
   python main.py
   ```

4. **Access the API**
   - Service: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

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

1. **"File too large" Error**
   - Compress your video or use a shorter clip
   - Maximum file size is 100MB

2. **"Unsupported file format" Error**
   - Convert to supported format: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V

3. **Slow Processing**
   - First request loads the AI model (30-60 seconds)
   - Subsequent requests are faster
   - Longer videos take more time

4. **"Transcription not found" Error**
   - Transcriptions expire after 3.5 hours
   - Check if the ID is correct

5. **Rate Limit Exceeded**
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
