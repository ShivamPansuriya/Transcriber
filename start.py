#!/usr/bin/env python3
"""
Development startup script for Video Transcription Service
"""

import subprocess
import sys
import os
import time
import requests

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import whisper
        import ffmpeg
        print("✅ Python packages installed")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found")
        print("Install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        return False
    
    return True

def start_server():
    """Start the development server"""
    print("\nStarting Video Transcription Service...")
    print("=" * 50)
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
        
        # Wait for server to start
        print("Waiting for server to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:8000/health', timeout=1)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
            print(f"  Attempt {i+1}/30...")
        else:
            print("❌ Server failed to start within 30 seconds")
            process.terminate()
            return False
        
        print("\n🚀 Server started successfully!")
        print("=" * 50)
        print("📍 Service URL: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("=" * 50)
        print("\nPress Ctrl+C to stop the server")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\nStopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def main():
    print("Video Transcription Service - Development Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Make sure you're in the project directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()
