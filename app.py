from flask import Flask, request, jsonify, send_file
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename
import subprocess
import tempfile
from pathlib import Path

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_output'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Store processing status
processing_status = {}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_audio_ffmpeg(video_path, audio_path):
    """Extract audio using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn',  # No video
            '-acodec', 'mp3',  # Audio codec
            '-ab', '192k',  # Audio bitrate
            '-ar', '44100',  # Audio sample rate
            '-y',  # Overwrite output file
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return True, "Audio extracted successfully"
        else:
            return False, f"FFmpeg error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Processing timeout (5 minutes exceeded)"
    except Exception as e:
        return False, f"Error during extraction: {str(e)}"

def process_video_async(task_id, video_path, audio_path):
    """Process video extraction in background"""
    try:
        processing_status[task_id]['status'] = 'processing'
        
        # Extract audio
        success, message = extract_audio_ffmpeg(video_path, audio_path)
        
        if success:
            processing_status[task_id]['status'] = 'completed'
            processing_status[task_id]['audio_path'] = audio_path
        else:
            processing_status[task_id]['status'] = 'failed'
            processing_status[task_id]['error'] = message
            
    except Exception as e:
        processing_status[task_id]['status'] = 'failed'
        processing_status[task_id]['error'] = str(e)
    
    finally:
        # Always delete the video file
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            print(f"Error deleting video file: {e}")

def cleanup_old_files():
    """Clean up old files periodically"""
    while True:
        try:
            current_time = time.time()
            
            # Clean up old processing status (older than 1 hour)
            expired_tasks = []
            for task_id, task_info in processing_status.items():
                if current_time - task_info.get('created_at', 0) > 3600:  # 1 hour
                    expired_tasks.append(task_id)
            
            for task_id in expired_tasks:
                del processing_status[task_id]
            
            # Clean up orphaned files
            for folder in [UPLOAD_FOLDER, AUDIO_FOLDER]:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            file_age = current_time - os.path.getctime(file_path)
                            if file_age > 3600:  # Delete files older than 1 hour
                                try:
                                    os.remove(file_path)
                                except Exception as e:
                                    print(f"Error deleting old file {file_path}: {e}")
            
        except Exception as e:
            print(f"Error in cleanup: {e}")
        
        time.sleep(300)  # Run every 5 minutes

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Video to Audio Extraction API',
        'endpoints': {
            'upload': 'POST /upload - Upload video file',
            'status': 'GET /status/<task_id> - Check processing status',
            'download': 'GET /audio/<task_id> - Download extracted audio'
        }
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({
                'error': 'Invalid file type',
                'allowed_types': list(ALLOWED_VIDEO_EXTENSIONS)
            }), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Secure filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        
        # Create unique filenames
        video_filename = f"{task_id}.{file_extension}"
        audio_filename = f"{task_id}.mp3"
        
        video_path = os.path.join(UPLOAD_FOLDER, video_filename)
        audio_path = os.path.join(AUDIO_FOLDER, audio_filename)
        
        # Save uploaded video
        file.save(video_path)
        
        # Check file size after saving
        if os.path.getsize(video_path) > MAX_FILE_SIZE:
            os.remove(video_path)
            return jsonify({'error': 'File too large (max 100MB)'}), 400
        
        # Initialize processing status
        processing_status[task_id] = {
            'status': 'queued',
            'created_at': time.time(),
            'original_filename': original_filename
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_video_async,
            args=(task_id, video_path, audio_path)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'queued',
            'original_filename': original_filename,
            'message': 'Video uploaded successfully. Processing started.'
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    task_info = processing_status[task_id]
    
    response = {
        'task_id': task_id,
        'status': task_info['status'],
        'original_filename': task_info.get('original_filename', '')
    }
    
    if task_info['status'] == 'failed':
        response['error'] = task_info.get('error', 'Unknown error')
    elif task_info['status'] == 'completed':
        response['message'] = 'Audio extraction completed. Ready for download.'
    
    return jsonify(response)

@app.route('/audio/<task_id>', methods=['GET'])
def download_audio(task_id):
    try:
        if task_id not in processing_status:
            return jsonify({'error': 'Task not found'}), 404
        
        task_info = processing_status[task_id]
        
        if task_info['status'] != 'completed':
            return jsonify({
                'error': 'Audio not ready',
                'status': task_info['status']
            }), 400
        
        audio_path = task_info.get('audio_path')
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Get original filename for download
        original_name = task_info.get('original_filename', 'audio')
        audio_filename = f"{os.path.splitext(original_name)[0]}.mp3"
        
        def remove_files():
            """Remove files after sending"""
            time.sleep(1)  # Brief delay to ensure file is sent
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                if task_id in processing_status:
                    del processing_status[task_id]
            except Exception as e:
                print(f"Error cleaning up files: {e}")
        
        # Schedule cleanup
        cleanup_thread = threading.Thread(target=remove_files)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        return send_file(
            audio_path,
            as_attachment=True,
            download_name=audio_filename,
            mimetype='audio/mpeg'
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)