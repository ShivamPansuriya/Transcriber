#!/usr/bin/env python3
"""
Setup script for Video Transcription Service
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install 'numpy<2.0.0'", "Installing compatible NumPy version"),
        ("pip install -r requirements.txt", "Installing Python packages")
    ]

    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found")
        return False

def install_ffmpeg_instructions():
    """Show FFmpeg installation instructions"""
    system = platform.system().lower()
    
    print("\n📋 FFmpeg Installation Instructions:")
    print("=" * 40)
    
    if system == "windows":
        print("Windows:")
        print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
        print("2. Extract to C:\\ffmpeg")
        print("3. Add C:\\ffmpeg\\bin to your PATH environment variable")
        print("4. Restart your terminal/command prompt")
    elif system == "darwin":  # macOS
        print("macOS:")
        print("1. Install Homebrew if not already installed:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("2. Install FFmpeg:")
        print("   brew install ffmpeg")
    else:  # Linux
        print("Linux (Ubuntu/Debian):")
        print("   sudo apt-get update && sudo apt-get install ffmpeg")
        print("\nLinux (CentOS/RHEL):")
        print("   sudo yum install ffmpeg")
        print("\nLinux (Arch):")
        print("   sudo pacman -S ffmpeg")

def create_virtual_environment():
    """Create and activate virtual environment"""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    print("\n📝 To activate the virtual environment:")
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    return True

def main():
    print("🚀 Video Transcription Service Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    print("\n1. Setting up virtual environment...")
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install Python dependencies
    print("\n2. Installing Python dependencies...")
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        print("\n💡 Try running these commands manually:")
        print("   pip install --upgrade pip")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Check FFmpeg
    print("\n3. Checking FFmpeg...")
    if not check_ffmpeg():
        install_ffmpeg_instructions()
        print("\n⚠️  Please install FFmpeg and run this setup again")
        sys.exit(1)
    
    # Success
    print("\n🎉 Setup completed successfully!")
    print("=" * 40)
    print("\n📋 Next steps:")
    print("1. Activate virtual environment (if not already active)")
    if platform.system().lower() == "windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start the service:")
    print("   python start.py")
    print("   OR")
    print("   python main.py")
    print("3. Open your browser to:")
    print("   http://localhost:8000/docs")
    print("\n📖 For deployment instructions, see DEPLOYMENT.md")

if __name__ == "__main__":
    main()
