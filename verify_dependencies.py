#!/usr/bin/env python3
"""
Dependency verification script for tubeMate Hugging Face Spaces deployment.
This script checks if all dependencies can be resolved without conflicts.
"""

import subprocess
import sys
import tempfile
import os

def check_dependencies(requirements_file):
    """Check if dependencies in requirements file can be resolved."""
    print(f"🔍 Checking dependencies in {requirements_file}...")
    
    try:
        # Create a temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = os.path.join(temp_dir, "test_venv")
            
            # Create virtual environment
            print("📦 Creating temporary virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", venv_path], 
                         check=True, capture_output=True)
            
            # Get pip path
            if os.name == 'nt':  # Windows
                pip_path = os.path.join(venv_path, "Scripts", "pip")
            else:  # Unix/Linux/macOS
                pip_path = os.path.join(venv_path, "bin", "pip")
            
            # Try to install dependencies
            print("⚡ Testing dependency resolution...")
            result = subprocess.run([
                pip_path, "install", "--dry-run", "-r", requirements_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ All dependencies can be resolved successfully!")
                return True
            else:
                print("❌ Dependency conflict detected:")
                print(result.stderr)
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during dependency check: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to check both requirements files."""
    print("🎬 tubeMate Dependency Verification")
    print("=" * 50)
    
    # Check main requirements.txt
    main_req = "requirements.txt"
    if os.path.exists(main_req):
        main_ok = check_dependencies(main_req)
    else:
        print(f"⚠️  {main_req} not found, skipping...")
        main_ok = True
    
    print()
    
    # Check HF Spaces requirements.txt
    hf_req = "hf_spaces_deploy/requirements.txt"
    if os.path.exists(hf_req):
        hf_ok = check_dependencies(hf_req)
    else:
        print(f"⚠️  {hf_req} not found, skipping...")
        hf_ok = True
    
    print()
    print("=" * 50)
    
    if main_ok and hf_ok:
        print("🎉 All dependency checks passed! Ready for deployment.")
        return 0
    else:
        print("💥 Dependency conflicts detected. Please fix before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
