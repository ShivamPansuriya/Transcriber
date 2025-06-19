# Deployment Guide for Render.com

This guide will help you deploy the Video-to-Audio API service to Render.com's free tier.

## Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Render.com Account**: Sign up at https://render.com (free)
3. **FFmpeg**: Automatically installed on Render.com

## Step-by-Step Deployment

### 1. Prepare Your Repository

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit: Video-to-Audio API"
git branch -M main
git remote add origin https://github.com/yourusername/video-to-audio-api.git
git push -u origin main
```

### 2. Deploy on Render.com

1. **Login to Render.com**
   - Go to https://render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code

3. **Configure Service**
   - **Name**: `video-to-audio-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 100 --max-requests-jitter 10 app:app`

4. **Environment Variables**
   - `FLASK_ENV`: `production`
   - `LOG_LEVEL`: `INFO`
   - `PYTHONUNBUFFERED`: `1`

5. **Advanced Settings**
   - **Plan**: Free
   - **Auto-Deploy**: Yes (recommended)
   - **Health Check Path**: `/health`

### 3. Docker Deployment (Automatic)

The included `Dockerfile` contains all the configuration. Render will automatically detect and use it:

1. Just push your code to GitHub (including the Dockerfile)
2. Connect the repository to Render
3. Render will automatically detect the Dockerfile and build a container
4. No manual configuration needed - FFmpeg is automatically installed!

### 4. Verify Deployment

Once deployed, your service will be available at:
```
https://your-service-name.onrender.com
```

Test the endpoints:
- Health check: `https://your-service-name.onrender.com/health`
- Stats: `https://your-service-name.onrender.com/stats`

## Testing Your Deployed Service

### Using curl

1. **Upload a video**:
```bash
curl -X POST \
  -F "file=@your_video.mp4" \
  https://your-service-name.onrender.com/upload
```

2. **Download the audio** (replace `audio-id` with the ID from step 1):
```bash
curl -O -J \
  https://your-service-name.onrender.com/audio/audio-id
```

### Using the Test Script

Run the test script against your deployed service:
```bash
python test_api.py https://your-service-name.onrender.com
```

## Free Tier Limitations

Render.com's free tier has these limitations:
- **512 MB RAM**: Service is optimized for this
- **Sleep after inactivity**: Service sleeps after 15 minutes of no requests
- **750 hours/month**: Plenty for testing and light usage
- **Cold starts**: First request after sleep takes ~30 seconds

## Monitoring Your Service

### Built-in Endpoints

- **Health Check**: `/health` - Service status and memory usage
- **Statistics**: `/stats` - Detailed service statistics
- **Logs**: Available in Render.com dashboard

### Render.com Dashboard

- View logs in real-time
- Monitor resource usage
- See deployment history
- Configure custom domains

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that `requirements.txt` is correct
   - Ensure Python version compatibility
   - Check build logs in Render dashboard

2. **Memory Issues**
   - Service automatically manages memory
   - Check `/stats` endpoint for memory usage
   - Large files may cause issues on free tier

3. **Timeout Issues**
   - Free tier has request timeouts
   - Large video files may timeout
   - Consider file size limits

4. **Cold Start Delays**
   - First request after sleep takes time
   - Subsequent requests are fast
   - Consider upgrading for always-on service

### Debugging

1. **Check Logs**:
   - Go to Render dashboard
   - Select your service
   - View "Logs" tab

2. **Test Endpoints**:
   - Use `/health` to check service status
   - Use `/stats` to monitor resource usage

3. **Local Testing**:
   - Test locally first: `python app.py`
   - Use test script: `python test_api.py`

## Scaling and Upgrades

### Free Tier Optimization
- Service is already optimized for 512MB RAM
- Automatic cleanup prevents memory leaks
- Single worker process minimizes overhead

### Paid Tier Benefits
- More RAM and CPU
- Always-on (no sleeping)
- Faster cold starts
- Higher request limits
- Custom domains

## Security Considerations

- No persistent file storage (files auto-deleted)
- Secure filename handling
- File type validation
- Request size limits
- No user data retention

## Support

- **Render.com Docs**: https://render.com/docs
- **Service Logs**: Available in Render dashboard
- **GitHub Issues**: Create issues in your repository

## Next Steps

After successful deployment:

1. **Test thoroughly** with various video formats
2. **Monitor resource usage** via `/stats` endpoint
3. **Set up monitoring** if needed
4. **Consider custom domain** for production use
5. **Implement rate limiting** if needed for high traffic

Your Video-to-Audio API is now ready for production use on Render.com! 🚀
