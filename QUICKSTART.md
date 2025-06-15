# Quick Start Guide

Get your Video Transcription Service running in 5 minutes!

## 🚀 Option 1: Automated Setup (Recommended)

```bash
# 1. Run the setup script
python setup.py

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Start the service (robust startup prevents restarts)
python start_robust.py
```

## 🛠️ Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install FFmpeg
# Windows: Download from https://ffmpeg.org/download.html
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# 5. Start the service
python start_robust.py  # Prevents restarts
# OR
python main.py         # Standard startup
```

## 🧪 Test Your Service

### Option A: Web Interface
1. Open http://localhost:8000/docs
2. Click "Try it out" on POST /transcribe
3. Upload a video file
4. Copy the returned ID
5. Use GET /transcribe/{id} to check status

### Option B: Command Line
```bash
# Test with example client
python example_client.py your_video.mp4

# Or test the API directly
python test_api.py your_video.mp4

# Monitor transcription progress in real-time
python log_monitor.py upload your_video.mp4
```

### Option C: cURL
```bash
# Upload video
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@your_video.mp4" \
  -F "language=en"

# Check status (replace 1 with your ID)
curl "http://localhost:8000/transcribe/1"
```

## 🌐 Deploy to Render.com

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main

# 2. Go to render.com
# 3. Create new Web Service
# 4. Connect your GitHub repo
# 5. Deploy!
```

## 📋 What You Get

- **Free transcription** using OpenAI Whisper
- **No API limits** - completely free
- **Multiple formats** - MP4, AVI, MOV, etc.
- **Auto language detection** or specify language
- **REST API** with automatic documentation
- **Rate limiting** and error handling
- **Ready for production** deployment

## 🔧 Configuration

Edit `config.py` to customize:
- File size limits
- Supported formats
- Whisper model size
- Rate limiting
- Cleanup intervals

## 📊 Monitoring & Logging

**Enable detailed logging:**
```bash
DEBUG=true python main.py
```

**Monitor transcription progress:**
```bash
# Test service
python log_monitor.py test

# Upload and monitor
python log_monitor.py upload video.mp4

# Monitor existing transcription
python log_monitor.py monitor 123
```

**Log to file:**
```bash
LOG_TO_FILE=true python main.py
```

## 📖 Need Help?

- **Full documentation**: See README.md
- **Deployment guide**: See DEPLOYMENT.md
- **API docs**: http://localhost:8000/docs (when running)
- **Health check**: http://localhost:8000/health

## 🎯 Common Issues

**"Service keeps restarting"**
- Run: `python start_robust.py` for automatic optimization
- See: [RESTART_TROUBLESHOOTING.md](RESTART_TROUBLESHOOTING.md)

**"NumPy compatibility error"**
- Run: `python fix_numpy.py` to fix automatically

**"FFmpeg not found"**
- Install FFmpeg for your OS (see setup instructions)

**"File too large"**
- Default limit is 100MB (configurable in config.py)

**"Service sleeping on Render"**
- Free tier sleeps after 15min inactivity (normal behavior)

**"Slow first request"**
- AI model loads on first use (30-60 seconds)

---

**Ready to transcribe? Your service is now running at http://localhost:8000! 🎉**
