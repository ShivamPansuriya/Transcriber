#!/usr/bin/env python3
"""
Real-time log monitor for Video Transcription Service
"""

import requests
import time
import sys
import json
from datetime import datetime

class TranscriptionMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.active_transcriptions = {}
    
    def monitor_transcription(self, transcription_id, poll_interval=5):
        """Monitor a specific transcription with real-time updates"""
        print(f"🔍 Monitoring transcription ID: {transcription_id}")
        print(f"⏱️ Poll interval: {poll_interval} seconds")
        print("=" * 50)
        
        start_time = time.time()
        last_status = None
        
        while True:
            try:
                response = requests.get(f"{self.base_url}/transcribe/{transcription_id}")
                
                if response.status_code == 404:
                    print(f"❌ Transcription {transcription_id} not found or expired")
                    break
                elif response.status_code != 200:
                    print(f"❌ Error checking status: {response.status_code}")
                    break
                
                result = response.json()
                status = result['status']
                elapsed = time.time() - start_time
                
                # Only print updates when status changes or every 30 seconds
                if status != last_status or elapsed % 30 < poll_interval:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] 📊 Status: {status.upper()} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        print("🎉 Transcription completed!")
                        print(f"🌐 Language: {result.get('language', 'N/A')}")
                        print(f"⏱️ Duration: {result.get('duration', 'N/A')} seconds")
                        text = result.get('text', '')
                        if text:
                            preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"📝 Text preview: {preview}")
                        break
                    elif status == 'failed':
                        print(f"❌ Transcription failed: {result.get('error_message', 'Unknown error')}")
                        break
                
                last_status = status
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(poll_interval)
    
    def list_active_transcriptions(self):
        """List all active transcriptions by checking health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health = response.json()
                active = health.get('active_transcriptions', 0)
                print(f"📊 Active transcriptions: {active}")
                return active
            else:
                print(f"❌ Cannot get health status: {response.status_code}")
                return 0
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            return 0
    
    def test_service(self):
        """Test if the service is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print("✅ Service is running")
                print(f"📊 Status: {health.get('status', 'unknown')}")
                print(f"📊 Active transcriptions: {health.get('active_transcriptions', 0)}")
                return True
            else:
                print(f"❌ Service returned status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to service at {self.base_url}")
            print("   Make sure the service is running with: python main.py")
            return False
        except Exception as e:
            print(f"❌ Error testing service: {e}")
            return False
    
    def upload_and_monitor(self, video_file, language=None):
        """Upload a video and monitor its transcription"""
        if not self.test_service():
            return
        
        print(f"📤 Uploading video: {video_file}")
        
        try:
            with open(video_file, 'rb') as f:
                files = {'file': f}
                data = {}
                if language:
                    data['language'] = language
                
                response = requests.post(f"{self.base_url}/transcribe", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                transcription_id = result['id']
                print(f"✅ Upload successful! ID: {transcription_id}")
                print()
                self.monitor_transcription(transcription_id)
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
        
        except FileNotFoundError:
            print(f"❌ Video file not found: {video_file}")
        except Exception as e:
            print(f"❌ Upload error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Video Transcription Service - Log Monitor")
        print("=" * 40)
        print("Usage:")
        print("  python log_monitor.py test                    # Test service")
        print("  python log_monitor.py monitor <id>            # Monitor transcription")
        print("  python log_monitor.py upload <video_file>     # Upload and monitor")
        print("  python log_monitor.py upload <video_file> <lang>  # Upload with language")
        print()
        print("Examples:")
        print("  python log_monitor.py test")
        print("  python log_monitor.py monitor 123")
        print("  python log_monitor.py upload video.mp4")
        print("  python log_monitor.py upload video.mp4 en")
        sys.exit(1)
    
    # Get API URL from environment or use default
    api_url = sys.argv[-1] if sys.argv[-1].startswith('http') else "http://localhost:8000"
    if api_url != "http://localhost:8000":
        sys.argv = sys.argv[:-1]  # Remove URL from args
    
    monitor = TranscriptionMonitor(api_url)
    command = sys.argv[1].lower()
    
    if command == "test":
        monitor.test_service()
        monitor.list_active_transcriptions()
    
    elif command == "monitor":
        if len(sys.argv) < 3:
            print("❌ Please provide transcription ID")
            print("Usage: python log_monitor.py monitor <id>")
            sys.exit(1)
        
        try:
            transcription_id = int(sys.argv[2])
            monitor.monitor_transcription(transcription_id)
        except ValueError:
            print("❌ Invalid transcription ID (must be a number)")
            sys.exit(1)
    
    elif command == "upload":
        if len(sys.argv) < 3:
            print("❌ Please provide video file")
            print("Usage: python log_monitor.py upload <video_file> [language]")
            sys.exit(1)
        
        video_file = sys.argv[2]
        language = sys.argv[3] if len(sys.argv) > 3 else None
        monitor.upload_and_monitor(video_file, language)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: test, monitor, upload")
        sys.exit(1)

if __name__ == "__main__":
    main()
