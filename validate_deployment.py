#!/usr/bin/env python3
"""
Validation script for deployment readiness
"""

import os
import sys

def check_file_exists(filename, description):
    """Check if a file exists and report"""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ Missing {description}: {filename}")
        return False

def check_dockerfile():
    """Validate Dockerfile contents"""
    if not os.path.exists('Dockerfile'):
        return False
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    required_elements = [
        ('FROM python:', 'Base Python image'),
        ('RUN apt-get update', 'System package installation'),
        ('ffmpeg', 'FFmpeg installation'),
        ('COPY requirements.txt', 'Requirements copy'),
        ('RUN pip install', 'Python package installation'),
        ('COPY . .', 'Application code copy'),
        ('CMD', 'Application start command'),
        ('gunicorn', 'Gunicorn server'),
    ]
    
    print("\n📋 Dockerfile validation:")
    all_good = True
    for element, description in required_elements:
        if element in content:
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description}")
            all_good = False
    
    return all_good

def check_requirements():
    """Check requirements.txt"""
    if not os.path.exists('requirements.txt'):
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'Flask',
        'ffmpeg-python',
        'gunicorn',
    ]
    
    print("\n📦 Requirements validation:")
    all_good = True
    for package in required_packages:
        if package in content:
            print(f"✅ {package}")
        else:
            print(f"❌ Missing package: {package}")
            all_good = False
    
    return all_good

def check_app_structure():
    """Check application structure"""
    required_files = [
        ('app.py', 'Main application file'),
        ('config.py', 'Configuration file'),
        ('audio_processor.py', 'Audio processing module'),
        ('file_manager.py', 'File management module'),
        ('utils.py', 'Utility functions'),
    ]
    
    print("\n🏗️  Application structure:")
    all_good = True
    for filename, description in required_files:
        if check_file_exists(filename, description):
            continue
        else:
            all_good = False
    
    return all_good

def check_app_endpoints():
    """Check if main endpoints are defined in app.py"""
    if not os.path.exists('app.py'):
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    required_endpoints = [
        ('@app.route(\'/upload\'', 'Upload endpoint'),
        ('@app.route(\'/audio/', 'Audio download endpoint'),
        ('@app.route(\'/health\'', 'Health check endpoint'),
        ('@app.route(\'/stats\'', 'Statistics endpoint'),
    ]
    
    print("\n🌐 API endpoints:")
    all_good = True
    for endpoint, description in required_endpoints:
        if endpoint in content:
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {description}")
            all_good = False
    
    return all_good

def main():
    """Main validation function"""
    print("🔍 Validating deployment readiness for Render.com")
    print("=" * 50)
    
    checks = [
        check_app_structure(),
        check_dockerfile(),
        check_requirements(),
        check_app_endpoints(),
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All validation checks passed!")
        print("\n✅ Your application is ready for deployment to Render.com")
        print("\n📋 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Connect the repository to Render.com")
        print("3. Render will automatically detect the Dockerfile")
        print("4. Your service will be deployed with FFmpeg pre-installed")
        return 0
    else:
        print("❌ Some validation checks failed!")
        print("\n🔧 Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
