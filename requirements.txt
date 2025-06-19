# Video to Audio Extraction API

A simple Flask API that extracts audio from video files using FFmpeg. Videos are automatically deleted after audio extraction, and audio files are deleted after download.

## Features

- Upload video files (MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V)
- Extract audio to MP3 format
- Automatic file cleanup
- Asynchronous processing
- RESTful API with task tracking

## API Endpoints

### 1. Upload Video
```
POST /upload
```
Upload a video file for audio extraction.

**Request:**
- Content-Type: multipart/form-data
- Body: video file (max 100MB)

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "queued",
  "original_filename": "video.mp4",
  "message": "Video uploaded successfully. Processing started."
}
```

### 2. Check Status
```
GET /status/<task_id>
```
Check the processing status of your video.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed|processing|queued|failed",
  "original_filename": "video.mp4"
}
```

### 3. Download Audio
```
GET /audio/<task_id>
```
Download the extracted audio file. **Note:** Audio file is deleted after download.

**Response:**
- Content-Type: audio/mpeg
- File download (MP3 format)

## Usage Example

### Using curl:

1. **Upload video:**
```bash
curl -X POST -F "video=@your-video.mp4" http://your-app-url/upload
```

2. **Check status:**
```bash
curl http://your-app-url/status/YOUR_TASK_ID
```

3. **Download audio:**
```bash
curl -O -J http://your-app-url/audio/YOUR_TASK_ID
```

### Using Python requests:

```python
import requests
import time

# Upload video
with open('video.mp4', 'rb') as f:
    response = requests.post('http://your-app-url/upload', files={'video': f})
    task_id = response.json()['task_id']

# Wait for processing
while True:
    status = requests.get(f'http://your-app-url/status/{task_id}').json()
    if status['status'] == 'completed':
        break
    elif status['status'] == 'failed':
        print(f"Error: {status['error']}")
        exit()
    time.sleep(5)

# Download audio
audio_response = requests.get(f'http://your-app-url/audio/{task_id}')
with open('extracted_audio.mp3', 'wb') as f:
    f.write(audio_response.content)
```

## Deployment on Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository** containing these files
3. **Configure the service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 app:app`
   - Environment: `Python 3`

4. **Add environment variables** (if needed):
   - `PORT` (automatically set by Render)

5. **Deploy** and wait for the build to complete

### Alternative: Docker Deployment on Render

1. Make sure your repository has the Dockerfile
2. In Render, select **Docker** as the environment
3. Render will automatically detect and use the Dockerfile

## File Structure

```
project/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration (optional)
└── README.md          # This file
```

## Important Notes

- **File Limits:** Maximum file size is 100MB
- **Cleanup:** Video files are deleted immediately after processing
- **Cleanup:** Audio files are deleted after download
- **Cleanup:** Old files and tasks are automatically cleaned up after 1 hour
- **Processing Time:** Large files may take several minutes to process
- **Supported Formats:** MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V

## Dependencies

- **Flask:** Web framework
- **FFmpeg:** Audio/video processing (installed via system packages)
- **Gunicorn:** WSGI server for production

## Security Considerations

- File type validation
- File size limits
- Secure filename handling
- Automatic cleanup to prevent disk space issues
- No persistent storage of user files

## Troubleshooting

1. **"Task not found" error:** The task may have expired (> 1 hour old)
2. **"Audio not ready" error:** Processing is still in progress, check status again
3. **Large file uploads:** May take longer to process, be patient
4. **FFmpeg errors:** Check that the video file is not corrupted

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (system dependency)
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from https://ffmpeg.org/

# Run the application
python app.py
```

The API will be available at `http://localhost:5000`