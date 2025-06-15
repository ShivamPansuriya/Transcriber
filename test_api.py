#!/usr/bin/env python3
"""
Simple test script for the Video Transcription Service
"""

import requests
import time
import sys
import os

def test_transcription_service(base_url="http://localhost:8000", video_file=None):
    """Test the transcription service with a video file"""
    
    print(f"Testing Video Transcription Service at {base_url}")
    print("=" * 50)
    
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
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: File upload (if video file provided)
    if video_file and os.path.exists(video_file):
        print(f"\n3. Testing video upload with {video_file}...")
        try:
            with open(video_file, 'rb') as f:
                files = {'file': f}
                data = {'language': 'en'}
                response = requests.post(f"{base_url}/transcribe", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                transcription_id = result['id']
                print("✅ Video upload successful")
                print(f"   Transcription ID: {transcription_id}")
                print(f"   Status: {result['status']}")
                
                # Test 4: Check transcription status
                print(f"\n4. Checking transcription status...")
                max_attempts = 30  # Wait up to 5 minutes
                for attempt in range(max_attempts):
                    try:
                        response = requests.get(f"{base_url}/transcribe/{transcription_id}")
                        if response.status_code == 200:
                            result = response.json()
                            status = result['status']
                            print(f"   Attempt {attempt + 1}: Status = {status}")
                            
                            if status == 'completed':
                                print("✅ Transcription completed!")
                                print(f"   Text: {result['text'][:100]}...")
                                print(f"   Language: {result.get('language', 'N/A')}")
                                print(f"   Duration: {result.get('duration', 'N/A')} seconds")
                                break
                            elif status == 'failed':
                                print(f"❌ Transcription failed: {result.get('error_message', 'Unknown error')}")
                                break
                            elif status in ['pending', 'processing']:
                                time.sleep(10)  # Wait 10 seconds before next check
                            else:
                                print(f"❌ Unknown status: {status}")
                                break
                        else:
                            print(f"❌ Status check failed: {response.status_code}")
                            break
                    except Exception as e:
                        print(f"❌ Status check error: {e}")
                        break
                else:
                    print("⏰ Transcription timed out (5 minutes)")
                    
            else:
                print(f"❌ Video upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Video upload error: {e}")
    else:
        print(f"\n3. Skipping video upload test (no video file provided)")
        print(f"   To test with a video file, run: python test_api.py <video_file>")
    
    # Test 5: Invalid transcription ID
    print(f"\n5. Testing invalid transcription ID...")
    try:
        response = requests.get(f"{base_url}/transcribe/99999")
        if response.status_code == 404:
            print("✅ Invalid ID handling works correctly")
        else:
            print(f"❌ Invalid ID test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid ID test error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    return True

if __name__ == "__main__":
    # Get base URL from environment or use default
    base_url = os.getenv("API_URL", "http://localhost:8000")
    
    # Get video file from command line argument
    video_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    if video_file and not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found")
        sys.exit(1)
    
    success = test_transcription_service(base_url, video_file)
    sys.exit(0 if success else 1)
