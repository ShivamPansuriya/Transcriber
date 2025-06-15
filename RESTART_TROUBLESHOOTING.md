# Restart Troubleshooting Guide

If your Video Transcription Service is getting restarted frequently, this guide will help you identify and fix the issue.

## 🔍 **Common Restart Causes**

### 1. **Memory Exhaustion (Most Common)**
**Symptoms:**
- Service restarts during model loading
- Restarts when processing large videos
- "Process killed (signal 9)" in logs

**Solutions:**
```bash
# Use tiny model (uses less memory)
WHISPER_MODEL=tiny python main.py

# Or use the robust startup script
python start_robust.py
```

### 2. **Request Timeouts**
**Symptoms:**
- Restarts during first transcription request
- Long delays before restart
- No error messages, just restart

**Solutions:**
```bash
# Enable model preloading
MODEL_PRELOAD=true python main.py

# Use robust startup (preloads automatically)
python start_robust.py
```

### 3. **Dependency Issues**
**Symptoms:**
- Restarts immediately after startup
- Import errors in logs
- NumPy compatibility errors

**Solutions:**
```bash
# Fix NumPy compatibility
python fix_numpy.py

# Reinstall dependencies
pip install -r requirements.txt
```

## 🛠️ **Quick Fixes**

### **Option 1: Use Robust Startup (Recommended)**
```bash
python start_robust.py
```
This script automatically:
- Detects your environment (local/cloud/Render)
- Sets optimal configuration
- Preloads the model
- Uses memory-efficient settings

### **Option 2: Manual Configuration**
```bash
# For free tier / limited memory
WHISPER_MODEL=tiny MODEL_PRELOAD=true DEBUG=false python main.py

# For local development
WHISPER_MODEL=base MODEL_PRELOAD=true python main.py
```

### **Option 3: Environment Variables**
Create a `.env` file:
```env
WHISPER_MODEL=tiny
MODEL_PRELOAD=true
DEBUG=false
MAX_FILE_SIZE=52428800
```

## 📊 **Memory Optimization**

### **Model Size Comparison**
| Model | Memory Usage | Speed | Accuracy |
|-------|-------------|-------|----------|
| tiny  | ~39MB      | Fast  | Good     |
| base  | ~74MB      | Medium| Better   |
| small | ~244MB     | Slow  | Best     |

**For free tier (512MB RAM limit): Use `tiny`**

### **File Size Limits**
```bash
# Conservative (recommended for free tier)
MAX_FILE_SIZE=50MB

# Standard (for paid tiers)
MAX_FILE_SIZE=100MB
```

## 🔧 **Render.com Specific Fixes**

### **Update render.yaml**
```yaml
services:
  - type: web
    name: video-transcription-service
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    envVars:
      - key: WHISPER_MODEL
        value: tiny
      - key: MODEL_PRELOAD
        value: true
      - key: DEBUG
        value: false
    healthCheckPath: /health
    autoDeploy: true
```

### **Dockerfile Optimization**
The updated Dockerfile now includes:
- Memory-efficient settings
- Model preloading
- Robust startup script

## 📋 **Diagnostic Commands**

### **Check Service Health**
```bash
curl http://localhost:8000/health
```

**Healthy Response:**
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "model_name": "tiny",
  "active_transcriptions": 0
}
```

### **Monitor Memory Usage**
```bash
# Local monitoring
python -c "
import psutil
p = psutil.Process()
print(f'Memory: {p.memory_info().rss / 1024**2:.1f}MB')
"
```

### **Test Model Loading**
```bash
python -c "
import whisper
import time
start = time.time()
model = whisper.load_model('tiny')
print(f'Loaded in {time.time()-start:.1f}s')
"
```

## 🚨 **Emergency Fixes**

### **If Service Won't Start**
1. **Check dependencies:**
   ```bash
   python -c "import fastapi, whisper, torch; print('OK')"
   ```

2. **Fix NumPy issues:**
   ```bash
   python fix_numpy.py
   ```

3. **Use minimal configuration:**
   ```bash
   WHISPER_MODEL=tiny DEBUG=false python main.py
   ```

### **If Restarts During Requests**
1. **Enable model preloading:**
   ```bash
   MODEL_PRELOAD=true python start_robust.py
   ```

2. **Reduce file size limit:**
   ```bash
   # Edit config.py
   MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
   ```

3. **Use tiny model:**
   ```bash
   WHISPER_MODEL=tiny python main.py
   ```

## 📈 **Performance Monitoring**

### **Log Analysis**
Look for these patterns in logs:

**Memory Issues:**
```
⚠️ High memory usage: 450.1MB (limit: 512MB)
```

**Model Loading:**
```
✅ Whisper model preloaded successfully in 15.2 seconds
```

**Successful Transcription:**
```
🎉 Transcription 1 completed successfully in 45.6 seconds total
```

### **Health Check Monitoring**
```bash
# Continuous monitoring
while true; do
  curl -s http://localhost:8000/health | jq '.model_status'
  sleep 30
done
```

## 🎯 **Best Practices**

### **For Free Tier Hosting**
1. Use `WHISPER_MODEL=tiny`
2. Enable `MODEL_PRELOAD=true`
3. Set `DEBUG=false`
4. Limit file sizes to 25-50MB
5. Process one video at a time

### **For Local Development**
1. Use `WHISPER_MODEL=base` or `small`
2. Enable `DEBUG=true` for detailed logs
3. Use `LOG_TO_FILE=true` for persistent logs
4. Monitor memory usage

### **For Production**
1. Use paid hosting with more memory
2. Enable model preloading
3. Set up proper monitoring
4. Use load balancing for multiple instances

## 🔄 **Restart Recovery**

### **Automatic Recovery**
The service includes automatic recovery features:
- Graceful shutdown handling
- Model preloading on startup
- Memory usage monitoring
- Optimal settings detection

### **Manual Recovery**
If the service keeps restarting:

1. **Check logs for error patterns**
2. **Reduce resource usage**
3. **Use robust startup script**
4. **Contact hosting support if needed**

## 📞 **Getting Help**

### **Log Collection**
When reporting issues, include:
```bash
# System info
python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'Platform: {platform.platform()}')"

# Memory info
python -c "import psutil; m=psutil.virtual_memory(); print(f'Memory: {m.total/1024**3:.1f}GB total, {m.available/1024**3:.1f}GB available')"

# Service health
curl http://localhost:8000/health
```

### **Common Solutions Summary**
| Problem | Solution |
|---------|----------|
| Memory exhaustion | Use `WHISPER_MODEL=tiny` |
| Request timeouts | Enable `MODEL_PRELOAD=true` |
| NumPy errors | Run `python fix_numpy.py` |
| Frequent restarts | Use `python start_robust.py` |
| Large file issues | Reduce `MAX_FILE_SIZE` |

---

**With these fixes, your service should run stably without restarts! 🎉**
