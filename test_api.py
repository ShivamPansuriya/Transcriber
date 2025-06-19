#!/usr/bin/env python3
"""
Simple test script for the video-to-audio API
"""

import requests
import os
import time

def test_api(base_url="http://localhost:5000"):
    """Test the API endpoints"""
    
    print("🧪 Testing Video-to-Audio API")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    print()
    
    # Test 2: Stats endpoint
    print("2. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint working")
            stats = response.json()
            print(f"   File manager stats: {stats.get('file_manager', {})}")
            print(f"   Memory usage: {stats.get('memory_mb', 'N/A')} MB")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    print()
    
    # Test 3: Upload without file (should fail)
    print("3. Testing upload without file (should fail)...")
    try:
        response = requests.post(f"{base_url}/upload")
        if response.status_code == 400:
            print("✅ Correctly rejected upload without file")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    
    print()
    
    # Test 4: Invalid audio ID (should fail)
    print("4. Testing invalid audio ID (should fail)...")
    try:
        response = requests.get(f"{base_url}/audio/invalid-id")
        if response.status_code == 404:
            print("✅ Correctly rejected invalid audio ID")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid ID test error: {e}")
    
    print()
    print("🎉 Basic API tests completed!")
    print("\nTo test with actual video files:")
    print("1. Create a small test video file")
    print("2. Use curl or a tool like Postman:")
    print(f'   curl -X POST -F "file=@test_video.mp4" {base_url}/upload')
    print("3. Use the returned audio_id to download:")
    print(f'   curl -O -J {base_url}/audio/{{audio_id}}')

def create_test_video():
    """Create a simple test video using ffmpeg (if available)"""
    print("\n📹 Creating test video...")
    
    # Check if ffmpeg is available
    if os.system("ffmpeg -version > /dev/null 2>&1") != 0:
        print("❌ FFmpeg not found. Cannot create test video.")
        print("   Install FFmpeg to create test videos automatically.")
        return None
    
    # Create a simple 5-second test video
    test_video_path = "test_video.mp4"
    cmd = (
        f'ffmpeg -f lavfi -i testsrc=duration=5:size=320x240:rate=1 '
        f'-f lavfi -i sine=frequency=1000:duration=5 '
        f'-c:v libx264 -c:a aac -shortest -y {test_video_path}'
    )
    
    print(f"Creating test video: {test_video_path}")
    if os.system(cmd) == 0:
        print(f"✅ Test video created: {test_video_path}")
        return test_video_path
    else:
        print("❌ Failed to create test video")
        return None

def test_full_workflow(base_url="http://localhost:5000"):
    """Test the complete upload and download workflow"""
    
    # Create test video
    test_video = create_test_video()
    if not test_video:
        print("⚠️  Skipping full workflow test (no test video)")
        return
    
    print("\n🔄 Testing full workflow...")
    
    try:
        # Upload video
        print("1. Uploading test video...")
        with open(test_video, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
        
        upload_result = response.json()
        audio_id = upload_result.get('audio_id')
        print(f"✅ Upload successful! Audio ID: {audio_id}")
        
        # Download audio
        print("2. Downloading extracted audio...")
        response = requests.get(f"{base_url}/audio/{audio_id}")
        
        if response.status_code != 200:
            print(f"❌ Download failed: {response.status_code}")
            return
        
        # Save downloaded audio
        audio_filename = f"downloaded_audio_{int(time.time())}.mp3"
        with open(audio_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Audio downloaded: {audio_filename}")
        print(f"   File size: {len(response.content)} bytes")
        
        # Try to download again (should fail - file deleted)
        print("3. Trying to download again (should fail)...")
        response = requests.get(f"{base_url}/audio/{audio_id}")
        
        if response.status_code == 404:
            print("✅ Correctly deleted audio file after first download")
        else:
            print(f"❌ Audio file not deleted: {response.status_code}")
        
        print("\n🎉 Full workflow test completed successfully!")
        
        # Cleanup
        if os.path.exists(test_video):
            os.remove(test_video)
            print(f"🧹 Cleaned up test video: {test_video}")
        
        if os.path.exists(audio_filename):
            print(f"📁 Downloaded audio saved as: {audio_filename}")
            print("   You can delete this file manually if needed.")
    
    except Exception as e:
        print(f"❌ Full workflow test error: {e}")
    
    finally:
        # Cleanup test video if it exists
        if test_video and os.path.exists(test_video):
            os.remove(test_video)

if __name__ == "__main__":
    import sys
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Run basic tests
    test_api(base_url)
    
    # Ask user if they want to run full workflow test
    if base_url == "http://localhost:5000":
        print("\n" + "="*50)
        response = input("Run full workflow test with test video? (y/N): ")
        if response.lower() in ['y', 'yes']:
            test_full_workflow(base_url)
    else:
        print(f"\n⚠️  Full workflow test skipped for remote URL: {base_url}")
        print("   Run locally to test with generated video files.")
