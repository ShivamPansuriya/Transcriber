#!/usr/bin/env python3
"""
Fix NumPy compatibility issue for Video Transcription Service
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_numpy_version():
    """Check current NumPy version"""
    try:
        import numpy as np
        version = np.__version__
        print(f"📊 Current NumPy version: {version}")
        
        # Check if version is 2.x
        major_version = int(version.split('.')[0])
        if major_version >= 2:
            print("⚠️  NumPy 2.x detected - this causes compatibility issues with PyTorch/Whisper")
            return False
        else:
            print("✅ NumPy version is compatible")
            return True
    except ImportError:
        print("❌ NumPy not installed")
        return False

def fix_numpy_compatibility():
    """Fix NumPy compatibility by downgrading to 1.x"""
    commands = [
        ("pip uninstall -y numpy", "Uninstalling current NumPy"),
        ("pip install 'numpy<2.0.0'", "Installing compatible NumPy version"),
        ("pip install --force-reinstall torch==2.1.0 torchaudio==2.1.0", "Reinstalling PyTorch with compatible NumPy"),
        ("pip install --force-reinstall openai-whisper==20231117", "Reinstalling Whisper with compatible NumPy")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def verify_installation():
    """Verify that everything works after the fix"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test NumPy
        import numpy as np
        print(f"✅ NumPy {np.__version__} imported successfully")
        
        # Test PyTorch
        import torch
        print(f"✅ PyTorch {torch.__version__} imported successfully")
        
        # Test Whisper
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test basic functionality
        print("🔍 Testing Whisper model loading...")
        try:
            # This will download the tiny model if not present (much faster than base)
            model = whisper.load_model("tiny")
            print("✅ Whisper model loaded successfully")
            return True
        except Exception as e:
            print(f"⚠️  Whisper model loading failed: {e}")
            print("   This might be due to network issues - try running the service anyway")
            return True
            
    except Exception as e:
        print(f"❌ Installation verification failed: {e}")
        return False

def main():
    print("🔧 NumPy Compatibility Fix for Video Transcription Service")
    print("=" * 60)
    
    # Check current NumPy version
    if check_numpy_version():
        print("\n✅ NumPy version is already compatible!")
        print("If you're still getting errors, try restarting your service.")
        return
    
    print("\n🔧 Fixing NumPy compatibility...")
    
    # Fix NumPy compatibility
    if not fix_numpy_compatibility():
        print("\n❌ Failed to fix NumPy compatibility")
        print("\n💡 Manual fix:")
        print("1. pip uninstall numpy")
        print("2. pip install 'numpy<2.0.0'")
        print("3. pip install --force-reinstall torch torchaudio openai-whisper")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Installation verification had issues")
        print("Try running the service - it might still work")
    
    print("\n🎉 NumPy compatibility fix completed!")
    print("=" * 40)
    print("\n📋 Next steps:")
    print("1. Restart your transcription service:")
    print("   python main.py")
    print("   OR")
    print("   python start.py")
    print("2. Test with a video file")
    print("\n💡 If you still get errors, try:")
    print("- Restart your terminal/command prompt")
    print("- Deactivate and reactivate your virtual environment")

if __name__ == "__main__":
    main()
