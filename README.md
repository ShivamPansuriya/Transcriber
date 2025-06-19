# Video-to-Audio Extraction API

A lightweight, memory-efficient API service that extracts audio from video files with automatic cleanup, optimized for Render.com's free tier (512MB RAM limit).

## Features

- **Video Upload & Audio Extraction**: Upload video files and get audio extracted automatically
- **Memory Optimized**: Immediate file cleanup and minimal memory footprint
- **Automatic Cleanup**: Files are deleted immediately after processing/serving
- **ID-based Access**: Secure file access using unique IDs
- **Multiple Formats**: Supports MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V, 3GP
- **Production Ready**: Configured for Render.com deployment

## API Endpoints

### POST `/upload`
Upload a video file and extract audio.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Video file in `file` field

**Response:**
```json
{
  "success": true,
  "audio_id": "unique-audio-id",
  "message": "Audio extracted successfully"
}
```

### GET `/audio/<audio_id>`
Download audio file by ID. **File is automatically deleted after download.**

**Request:**
- Method: `GET`
- Path: `/audio/{audio_id}`

**Response:**
- Audio file download (MP3 format)
- File is deleted immediately after successful download

### GET `/health`
Health check endpoint with service statistics.

### GET `/stats`
Get detailed service statistics and configuration.

## Quick Start

### Local Development

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install FFmpeg:**
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

3. **Run the Service:**
```bash
python app.py
```

The service will be available at `http://localhost:5000`

### Deploy to Render.com

1. **Connect Repository:**
   - Push this code to a GitHub repository
   - Connect the repository to Render.com

2. **Deploy:**
   - Render will automatically detect the `render.yaml` configuration
   - The service will be deployed with FFmpeg pre-installed
   - No additional configuration needed

## Usage Examples

### Upload Video and Extract Audio
```bash
curl -X POST \
  -F "file=@video.mp4" \
  http://your-service-url/upload
```

Response:
```json
{
  "success": true,
  "audio_id": "abc123-def456-ghi789",
  "message": "Audio extracted successfully"
}
```

### Download Audio File
```bash
curl -O -J \
  http://your-service-url/audio/abc123-def456-ghi789
```

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to `production` for deployment
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `PORT`: Server port (automatically set by Render.com)

### File Limits
- **Maximum file size**: 100MB
- **Supported formats**: MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V, 3GP
- **Output format**: MP3 (128kbps, stereo, 44.1kHz)

## Memory Management

The service is optimized for memory-constrained environments:

- **Immediate Cleanup**: Video files deleted after audio extraction
- **Auto-deletion**: Audio files deleted after download
- **Background Cleanup**: Orphaned files cleaned up automatically
- **Memory Monitoring**: Built-in memory usage logging
- **Efficient Processing**: Streaming file processing without loading into memory

## Architecture

- **Framework**: Flask (lightweight)
- **Audio Processing**: FFmpeg via ffmpeg-python
- **File Management**: In-memory ID mapping with automatic cleanup
- **Deployment**: Gunicorn WSGI server
- **Storage**: Temporary files with immediate cleanup

## Error Handling

The service includes comprehensive error handling:
- Invalid file formats
- File size limits
- Processing failures
- Missing files
- Memory constraints

## Monitoring

- Health check endpoint: `/health`
- Statistics endpoint: `/stats`
- Detailed logging with memory usage tracking
- Automatic cleanup reporting

## Security

- Secure filename handling
- File type validation
- Temporary file isolation
- Automatic cleanup prevents file accumulation
- No persistent storage of user files

## Limitations

- **Free Tier Optimized**: Designed for Render.com's 512MB RAM limit
- **Single Worker**: Uses one worker process to minimize memory usage
- **Temporary Storage**: Files are not persisted beyond processing
- **Processing Time**: Large files may take time to process

## Troubleshooting

### Common Issues

1. **File Too Large**: Reduce file size or split into smaller segments
2. **Unsupported Format**: Convert to supported format first
3. **Processing Timeout**: Large files may timeout on free tier
4. **Memory Issues**: Service automatically manages memory and cleanup

### Logs

Check application logs for detailed error information:
- File processing status
- Memory usage
- Cleanup operations
- Error details

## License

This project is open source and available under the MIT License.
