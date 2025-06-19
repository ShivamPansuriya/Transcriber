# Deployment Troubleshooting Guide

This guide helps resolve common deployment issues on Render.com.

## ✅ Pre-Deployment Checklist

Run the validation script before deploying:
```bash
python validate_deployment.py
```

## 🔧 Common Issues and Solutions

### 1. "No Dockerfile found" Error

**Problem**: Render can't find the Dockerfile
**Solution**: 
- Ensure `Dockerfile` is in the root directory
- Check that the file is named exactly `Dockerfile` (no extension)
- Verify the file was committed to Git

### 2. Build Fails During Package Installation

**Problem**: `pip install` fails during Docker build
**Solution**:
- Check `requirements.txt` syntax
- Ensure all package names are correct
- Try building locally if Docker is available:
  ```bash
  docker build -t test-app .
  ```

### 3. FFmpeg Not Found

**Problem**: Audio processing fails with FFmpeg errors
**Solution**:
- The Dockerfile automatically installs FFmpeg
- If issues persist, check the build logs in Render dashboard
- Verify the Dockerfile includes: `ffmpeg \` in the apt-get install command

### 4. FFmpeg "check" Parameter Error

**Problem**: Error: `run() got an unexpected keyword argument 'check'`
**Solution**:
- This was fixed in the latest version
- The issue was with ffmpeg-python 0.2.0 compatibility
- The fix removes the unsupported `check=True` parameter
- Error handling now properly captures FFmpeg output

### 4. Port Binding Issues

**Problem**: Service starts but isn't accessible
**Solution**:
- Render automatically sets the `PORT` environment variable
- The Dockerfile uses `${PORT:-10000}` to handle this
- Don't hardcode port numbers in your application

### 5. Memory Issues (Out of Memory)

**Problem**: Service crashes due to memory limits
**Solution**:
- The service is optimized for 512MB RAM
- Check memory usage via `/stats` endpoint
- Reduce file size limits if needed
- Ensure automatic cleanup is working

### 6. File Upload Fails

**Problem**: Large file uploads fail or timeout
**Solution**:
- Free tier has request timeouts (~30 seconds)
- Reduce max file size in `config.py`
- Test with smaller files first
- Check Render logs for specific error messages

### 7. Service Goes to Sleep

**Problem**: First request after inactivity is slow
**Solution**:
- This is normal behavior on free tier
- Service sleeps after 15 minutes of inactivity
- First request takes ~30 seconds (cold start)
- Subsequent requests are fast

## 🔍 Debugging Steps

### 1. Check Render Logs
1. Go to Render.com dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages during build or runtime

### 2. Test Endpoints
After deployment, test these endpoints:
```bash
# Health check
curl https://your-service.onrender.com/health

# Stats
curl https://your-service.onrender.com/stats

# Upload test (should fail without file)
curl -X POST https://your-service.onrender.com/upload
```

### 3. Local Testing
Test locally before deploying:
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Test with test script
python test_api.py
```

## 📊 Monitoring Your Service

### Health Monitoring
- Use `/health` endpoint for basic health checks
- Use `/stats` endpoint for detailed statistics
- Monitor memory usage regularly

### Performance Monitoring
- Check response times via Render dashboard
- Monitor error rates in logs
- Watch for memory usage spikes

## 🚨 Emergency Fixes

### Service Won't Start
1. Check build logs for errors
2. Verify all required files are present
3. Test locally if possible
4. Redeploy from a known working commit

### High Memory Usage
1. Check `/stats` endpoint
2. Look for memory leaks in logs
3. Restart the service via Render dashboard
4. Consider reducing concurrent requests

### File Cleanup Issues
1. Check background cleanup logs
2. Verify file manager is working
3. Manually trigger cleanup via service restart

## 📞 Getting Help

### Render.com Support
- Check Render.com documentation
- Use Render community forums
- Contact Render support for platform issues

### Application Issues
- Check application logs first
- Use the test script to isolate issues
- Review the troubleshooting steps above

### Common Error Messages

**"Application failed to respond"**
- Check if the service is binding to the correct port
- Verify the health check endpoint works
- Look for startup errors in logs

**"Build failed"**
- Check Dockerfile syntax
- Verify all dependencies are available
- Look at build logs for specific errors

**"Out of memory"**
- Service exceeded 512MB limit
- Check for memory leaks
- Reduce concurrent processing

## 🔄 Redeployment

If issues persist:
1. Make necessary fixes
2. Commit changes to Git
3. Push to GitHub
4. Render will automatically redeploy
5. Monitor logs during deployment

## 📈 Optimization Tips

### For Better Performance
- Keep file sizes reasonable
- Monitor memory usage
- Use efficient file processing
- Implement proper error handling

### For Reliability
- Test thoroughly before deploying
- Monitor service health
- Implement proper logging
- Use automatic cleanup

Your service should now be running smoothly on Render.com! 🚀
