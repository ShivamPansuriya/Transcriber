# Deployment Guide

This guide covers deploying the Video Transcription Service to Render.com's free tier.

## Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com) (free)
3. **Git**: Installed on your local machine

## Step-by-Step Deployment

### 1. Prepare Your Repository

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - Video Transcription Service"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Render

1. **Go to Render Dashboard**
   - Visit [dashboard.render.com](https://dashboard.render.com)
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Choose "Build and deploy from a Git repository"

3. **Connect Repository**
   - Select your GitHub repository
   - Click "Connect"

4. **Configure Service**
   - **Name**: `video-transcription-service` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`

5. **Advanced Settings**
   - **Plan**: Free (automatically selected)
   - **Environment Variables**: None needed (auto-configured)
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: Yes (recommended)

6. **Deploy**
   - Click "Create Web Service"
   - Render will start building your service

### 3. Monitor Deployment

1. **Build Process**
   - Watch the build logs in real-time
   - First build takes 5-10 minutes (installing dependencies)
   - Look for "Build successful" message

2. **Deployment Status**
   - Service will show "Live" when ready
   - Initial startup may take 30-60 seconds (loading AI model)

3. **Test Your Service**
   - Your service URL: `https://your-service-name.onrender.com`
   - API docs: `https://your-service-name.onrender.com/docs`
   - Health check: `https://your-service-name.onrender.com/health`

## Configuration Details

### Automatic Configuration

The service is pre-configured for Render's free tier:

- **Port**: Automatically uses `$PORT` environment variable
- **Memory**: Optimized for 512MB limit
- **CPU**: Efficient processing for shared CPU
- **Storage**: No persistent storage (in-memory only)
- **Health Checks**: Configured at `/health` endpoint

### Free Tier Limitations

**Resource Limits:**
- 512MB RAM
- Shared CPU
- 750 hours/month (service sleeps after 15min inactivity)
- No persistent storage

**Service Behavior:**
- **Cold Starts**: 30-60 seconds after sleep
- **File Size**: 100MB maximum per video
- **Processing**: Sequential (one video at a time)
- **Storage**: 3.5 hours maximum per transcription

## Troubleshooting

### Common Build Issues

1. **Out of Memory During Build**
   ```
   Error: Process killed (out of memory)
   ```
   - This is rare but can happen with large dependencies
   - Try pushing smaller commits
   - Contact Render support if persistent

2. **FFmpeg Installation Failed**
   ```
   E: Unable to locate package ffmpeg
   ```
   - Check Dockerfile has correct apt-get commands
   - Ensure base image is correct (python:3.11-slim)

3. **Python Package Installation Failed**
   ```
   ERROR: Could not install packages
   ```
   - Check requirements.txt syntax
   - Ensure all package names are correct
   - Try removing version pins if needed

### Runtime Issues

1. **Service Won't Start**
   - Check runtime logs in Render dashboard
   - Look for Python import errors
   - Verify all dependencies are installed

2. **Health Check Failing**
   ```
   Health check failed
   ```
   - Service might be taking too long to start
   - Check if Whisper model is loading correctly
   - Verify `/health` endpoint is accessible

3. **Out of Memory at Runtime**
   ```
   Process killed (signal 9)
   ```
   - Large video files can cause this
   - Reduce MAX_FILE_SIZE in config.py
   - Use smaller Whisper model (tiny instead of base)

4. **Slow Processing**
   - First request loads AI model (30-60 seconds)
   - Subsequent requests are faster
   - Consider using smaller model for speed

### Service Sleeping

**Free Tier Behavior:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- This is normal for free tier

**Solutions:**
- Upgrade to paid plan for always-on service
- Use external monitoring to keep service awake
- Inform users about potential cold start delays

## Monitoring and Maintenance

### Logs

Access logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor for errors and performance

### Metrics

Monitor service health:
- Response times
- Error rates
- Memory usage
- Active transcriptions

### Updates

Deploy updates automatically:
1. Push changes to GitHub
2. Render auto-deploys from main branch
3. Monitor deployment in dashboard

## Scaling Considerations

### Free Tier Optimization

**Current Setup:**
- Single instance
- 512MB RAM
- Shared CPU
- In-memory storage

**Optimization Tips:**
- Use smaller Whisper model for speed
- Implement request queuing
- Add request size validation
- Monitor memory usage

### Upgrade Path

**Paid Plans Offer:**
- More RAM (1GB+)
- Dedicated CPU
- Always-on service
- Multiple instances
- Persistent storage options

## Security

### Current Security Features

- Rate limiting (10 requests/minute)
- File size validation
- File type validation
- No persistent file storage
- Automatic cleanup

### Additional Security (Optional)

- API key authentication
- HTTPS only (automatic on Render)
- Request logging
- IP whitelisting
- CORS configuration

## Support

### Getting Help

1. **Render Support**
   - Free tier includes community support
   - Check Render documentation
   - Use Render community forum

2. **Service Issues**
   - Check service logs first
   - Verify configuration
   - Test with smaller files

3. **API Issues**
   - Use `/docs` endpoint for testing
   - Check request format
   - Verify file types and sizes

### Useful Commands

```bash
# Test your deployed service
curl https://your-service.onrender.com/health

# Upload test video
curl -X POST "https://your-service.onrender.com/transcribe" \
  -F "file=@test.mp4"

# Check transcription status
curl "https://your-service.onrender.com/transcribe/1"
```

---

**Your service is now live and ready to transcribe videos! 🎉**

Share your service URL with users or integrate it into your applications.
