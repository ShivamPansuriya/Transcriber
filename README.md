# Video Transcription Service - tubeMate

This repository contains a complete video transcription service with support for both local deployment and Hugging Face Spaces deployment.

## 📁 Project Structure

All project files have been organized into the `tubeMate` folder:

```
tubeMate/
├── 📱 Core Application
│   ├── main.py                    # FastAPI application entry point
│   ├── app.py                     # Alternative Gradio+FastAPI app
│   ├── config.py                  # Configuration settings
│   ├── models.py                  # Pydantic data models
│   ├── storage.py                 # In-memory storage manager
│   ├── transcription_service.py   # Core transcription logic
│   ├── logging_config.py          # Logging configuration
│   └── restart_handler.py         # Service restart handling
│
├── 🚀 Deployment & Setup
│   ├── requirements.txt           # Python dependencies
│   ├── setup.py                   # Package setup
│   ├── Dockerfile                 # Container configuration
│   ├── start.py                   # Standard startup script
│   └── start_robust.py            # Robust startup with optimization
│
├── 🤗 Hugging Face Integration
│   ├── deploy_to_hf.py            # HF Spaces deployment script
│   ├── hf_api_client.py           # HF Spaces API client
│   └── hf_spaces_deploy/          # HF Spaces deployment files
│       ├── app.py                 # Gradio+FastAPI hybrid app
│       ├── config.py              # HF-optimized configuration
│       ├── requirements.txt       # HF Spaces dependencies
│       └── [other supporting files]
│
├── 🛠️ Utilities & Testing
│   ├── example_client.py          # Example API client
│   ├── test_api.py                # API testing script
│   ├── fix_numpy.py               # NumPy compatibility fix
│   └── log_monitor.py             # Log monitoring utility
│
└── 📚 Documentation
    ├── README.md                  # Main project documentation
    ├── README_HF.md               # Hugging Face specific docs
    ├── HF_MIGRATION_GUIDE.md      # Migration guide to HF Spaces
    ├── HF_DEPLOYMENT_SUMMARY.md   # HF deployment summary
    ├── QUICKSTART.md              # Quick start guide
    ├── DEPLOYMENT.md              # Deployment instructions
    ├── LOGGING_GUIDE.md           # Logging configuration guide
    └── RESTART_TROUBLESHOOTING.md # Troubleshooting guide
```

## 🚀 Quick Start

### Local Development
```bash
cd tubeMate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Standard startup
python app.py

# Or enhanced startup with port conflict resolution
python start_with_port_detection.py
```

### Hugging Face Spaces Deployment
```bash
cd tubeMate
python deploy_to_hf.py
# Follow the instructions in HF_MIGRATION_GUIDE.md
```

## 📖 Documentation

- **Main Documentation**: `tubeMate/README.md`
- **Hugging Face Guide**: `tubeMate/HF_MIGRATION_GUIDE.md`
- **Quick Start**: `tubeMate/QUICKSTART.md`
- **Deployment**: `tubeMate/DEPLOYMENT.md`

## 🎯 Features

- 🎥 Multiple video format support (MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V)
- 🗣️ Free speech-to-text using OpenAI Whisper
- 🌐 REST API with async processing
- 🤗 Hugging Face Spaces integration with Gradio interface
- ⚡ Rate limiting and auto cleanup
- 📝 Comprehensive logging and monitoring

## 🔧 Enhanced Features

### **Recent Improvements:**
- ✅ **Port Conflict Resolution**: Automatically finds available ports (no more "address already in use" errors)
- ✅ **Smart Startup**: Enhanced startup scripts with port management
- ✅ **Dependency Fixes**: Resolved Gradio compatibility issues
- ✅ **Better Organization**: All files organized in tubeMate folder

### **Cleaned Up:**
- Removed `__pycache__/` directory (Python cache files)
- Removed `render.yaml` (Render.com specific configuration)
- Fixed dependency conflicts for Hugging Face Spaces deployment

---

**To get started, navigate to the `tubeMate` folder and follow the documentation there!**
