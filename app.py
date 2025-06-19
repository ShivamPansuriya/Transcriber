from flask import Flask, request, jsonify, send_file
import os
import uuid
import threading
import time
from werkzeug.utils import secure_filename
import subprocess
import logging
from pathlib import Path

# ------------------- Logging Configuration -------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------- Flask App Setup -------------------
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_output'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

processing_status = {}

# ------------------- Helper Functions -------------------
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_audio_ffmpeg(video_path, audio_path):
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'mp3', '-ab', '192k',
            '-ar', '44100', '-y', audio_path
        ]
        logger.info(f"Running ffmpeg command for {video_path}")
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
    try:
        logger.info(f"[{task_id}] Started audio extraction thread.")
        processing_status[task_id]['status'] = 'processing'
        success, message = extract_audio_ffmpeg(video_path, audio_path)
        if success:
            processing_status[task_id]['status'] = 'completed'
            processing_status[task_id]['audio_path'] = audio_path
            logger.info(f"[{task_id}] Extraction completed.")
        else:
            processing_status[task_id]['status'] = 'failed'
            processing_status[task_id]['error'] = message
            logger.error(f"[{task_id}] Extraction failed: {message}")
    except Exception as e:
        processing_status[task_id]['status'] = 'failed'
        processing_status[task_id]['error'] = str(e)
        logger.exception(f"[{task_id}] Unexpected error.")
    finally:
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"[{task_id}] Deleted video file: {video_path}")
        except Exception as e:
            logger.warning(f"[{task_id}] Error deleting video: {e}")

def cleanup_old_files():
    while True:
        try:
            current_time = time.time()
            expired_tasks = [tid for tid, info in processing_status.items()
                             if current_time - info.get('created_at', 0) > 3600]
            for tid in expired_tasks:
                logger.info(f"Cleaning up expired task: {tid}")
                processing_status.pop(tid, None)
            for folder in [UPLOAD_FOLDER, AUDIO_FOLDER]:
                for fname in os.listdir(folder):
                    fpath = os.path.join(folder, fname)
                    if os.path.isfile(fpath) and time.time() - os.path.getctime(fpath) > 3600:
                        try:
                            os.remove(fpath)
                            logger.debug(f"Deleted old file: {fpath}")
                        except Exception as e:
                            logger.warning(f"Failed to delete file {fpath}: {e}")
        except Exception as e:
            logger.error(f"Cleanup thread error: {e}")
        time.sleep(300)

cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

# ------------------- API Endpoints -------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Video to Audio Extraction API',
        'endpoints': {
            'upload': 'POST /upload - Upload video file',
            'status': 'GET /status/<task_id>',
            'download': 'GET /audio/<task_id>'
        }
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        logger.info("Upload request received.")
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        file = request.files['video']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        is_valid = allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS) or (
            file.content_type and 'video' in file.content_type.lower()
        )
        if not is_valid:
            return jsonify({'error': 'Invalid file type'}), 400

        task_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'mp4'
        video_path = os.path.join(UPLOAD_FOLDER, f"{task_id}.{file_extension}")
        audio_path = os.path.join(AUDIO_FOLDER, f"{task_id}.mp3")
        file.save(video_path)

        if os.path.getsize(video_path) > MAX_FILE_SIZE:
            os.remove(video_path)
            return jsonify({'error': 'File too large (max 100MB)'}), 400

        processing_status[task_id] = {
            'status': 'queued',
            'created_at': time.time(),
            'original_filename': original_filename
        }

        threading.Thread(target=process_video_async, args=(task_id, video_path, audio_path), daemon=True).start()

        return jsonify({
            'task_id': task_id,
            'status': 'queued',
            'message': 'Video uploaded and processing started.'
        }), 202
    except Exception as e:
        logger.exception("Upload failed.")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    if task_id not in processing_status:
        logger.warning(f"Status check for unknown task: {task_id}")
        return jsonify({'error': 'Task not found'}), 404
    task = processing_status[task_id]
    logger.info(f"Status for {task_id}: {task['status']}")
    response = {
        'task_id': task_id,
        'status': task['status'],
        'original_filename': task.get('original_filename', '')
    }
    if task['status'] == 'failed':
        response['error'] = task.get('error')
    elif task['status'] == 'completed':
        response['message'] = 'Audio extraction completed.'
    return jsonify(response)

@app.route('/audio/<task_id>', methods=['GET'])
def download_audio(task_id):
    try:
        if task_id not in processing_status:
            logger.warning(f"Download request for missing task: {task_id}")
            return jsonify({'error': 'Task not found'}), 404
        task = processing_status[task_id]
        if task['status'] != 'completed':
            logger.info(f"Task {task_id} not ready for download. Status: {task['status']}")
            return jsonify({'error': 'Audio not ready', 'status': task['status']}), 400
        audio_path = task.get('audio_path')
        if not audio_path or not os.path.exists(audio_path):
            logger.error(f"Audio file missing for {task_id}")
            return jsonify({'error': 'Audio file not found'}), 404

        audio_filename = f"{os.path.splitext(task.get('original_filename', 'audio'))[0]}.mp3"

        def cleanup_file():
            time.sleep(1)
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logger.info(f"Deleted audio file: {audio_path}")
            except Exception as e:
                logger.warning(f"Error deleting file {audio_path}: {e}")

        threading.Thread(target=cleanup_file, daemon=True).start()

        logger.info(f"Serving audio for {task_id}")
        return send_file(audio_path, as_attachment=True, download_name=audio_filename, mimetype='audio/mpeg')

    except Exception as e:
        logger.exception("Download failed.")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

# ------------------- Error Handlers -------------------
@app.errorhandler(413)
def too_large(e):
    logger.warning("Upload too large.")
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    logger.warning("Invalid route.")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error("Internal server error.")
    return jsonify({'error': 'Internal server error'}), 500

# ------------------- Run -------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
