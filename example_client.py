#!/usr/bin/env python3
"""
Example client for the Video Transcription Service
Usage: python example_client.py <video_file> [language]
"""

import requests
import time
import sys
import os

class TranscriptionClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def transcribe_video(self, video_path, language=None, poll_interval=10, max_wait_minutes=10):
        """
        Transcribe a video file and wait for results
        
        Args:
            video_path: Path to video file
            language: Optional language code (e.g., 'en', 'es')
            poll_interval: Seconds between status checks
            max_wait_minutes: Maximum minutes to wait for completion
            
        Returns:
            dict: Transcription result or None if failed
        """
        
        if not os.path.exists(video_path):
            print(f"Error: Video file '{video_path}' not found")
            return None
        
        file_size = os.path.getsize(video_path)
        print(f"Uploading video: {video_path} ({file_size / (1024*1024):.1f} MB)")
        
        # Upload video
        try:
            with open(video_path, 'rb') as f:
                files = {'file': f}
                data = {}
                if language:
                    data['language'] = language
                
                print("Uploading...")
                response = requests.post(f"{self.base_url}/transcribe", files=files, data=data)
            
            if response.status_code != 200:
                print(f"Upload failed: {response.status_code}")
                print(response.text)
                return None
            
            result = response.json()
            transcription_id = result['id']
            print(f"Upload successful! Transcription ID: {transcription_id}")
            print(f"Status: {result['status']}")
            
        except Exception as e:
            print(f"Upload error: {e}")
            return None
        
        # Poll for results
        print(f"Waiting for transcription (checking every {poll_interval} seconds)...")
        max_attempts = (max_wait_minutes * 60) // poll_interval
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/transcribe/{transcription_id}")
                
                if response.status_code != 200:
                    print(f"Status check failed: {response.status_code}")
                    return None
                
                result = response.json()
                status = result['status']
                
                if status == 'completed':
                    print("✅ Transcription completed!")
                    return result
                elif status == 'failed':
                    print(f"❌ Transcription failed: {result.get('error_message', 'Unknown error')}")
                    return None
                elif status in ['pending', 'processing']:
                    print(f"⏳ Status: {status} (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(poll_interval)
                else:
                    print(f"❌ Unknown status: {status}")
                    return None
                    
            except Exception as e:
                print(f"Status check error: {e}")
                return None
        
        print(f"⏰ Transcription timed out after {max_wait_minutes} minutes")
        return None
    
    def get_transcription(self, transcription_id):
        """Get transcription by ID"""
        try:
            response = requests.get(f"{self.base_url}/transcribe/{transcription_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python example_client.py <video_file> [language] [api_url]")
        print("Examples:")
        print("  python example_client.py video.mp4")
        print("  python example_client.py video.mp4 en")
        print("  python example_client.py video.mp4 es https://your-service.onrender.com")
        sys.exit(1)
    
    video_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('http') else None
    api_url = sys.argv[3] if len(sys.argv) > 3 else sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].startswith('http') else "http://localhost:8000"
    
    print("Video Transcription Client")
    print("=" * 30)
    print(f"API URL: {api_url}")
    print(f"Video: {video_file}")
    print(f"Language: {language or 'auto-detect'}")
    print()
    
    client = TranscriptionClient(api_url)
    result = client.transcribe_video(video_file, language)
    
    if result:
        print("\n" + "=" * 50)
        print("TRANSCRIPTION RESULT")
        print("=" * 50)
        print(f"ID: {result['id']}")
        print(f"Language: {result.get('language', 'N/A')}")
        print(f"Duration: {result.get('duration', 'N/A')} seconds")
        print(f"Created: {result['created_at']}")
        print(f"Completed: {result.get('completed_at', 'N/A')}")
        print()
        print("TEXT:")
        print("-" * 20)
        print(result['text'])
        print()
        
        # Save to file
        output_file = f"{os.path.splitext(video_file)[0]}_transcription.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription of: {video_file}\n")
            f.write(f"Language: {result.get('language', 'N/A')}\n")
            f.write(f"Duration: {result.get('duration', 'N/A')} seconds\n")
            f.write(f"Created: {result['created_at']}\n")
            f.write(f"Completed: {result.get('completed_at', 'N/A')}\n")
            f.write("\n" + "=" * 50 + "\n")
            f.write(result['text'])
        
        print(f"💾 Transcription saved to: {output_file}")
    else:
        print("❌ Transcription failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
