import os
import tempfile
from flask import Flask, request, jsonify, send_file, after_this_request
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import config
from utils import handle_errors, setup_logging, log_memory_usage
from audio_processor import audio_processor
from file_manager import file_manager

# Initialize Flask app
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Setup logging
    logger = setup_logging(app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure file upload limits
    app.config['MAX_CONTENT_LENGTH'] = app.config.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024)
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return jsonify({
            'error': 'File too large',
            'message': 'Maximum file size is 100MB'
        }), 413
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        stats = file_manager.get_stats()
        memory_mb = log_memory_usage()
        
        return jsonify({
            'status': 'healthy',
            'service': 'video-to-audio-api',
            'file_stats': stats,
            'memory_mb': memory_mb
        })
    
    @app.route('/upload', methods=['POST'])
    @handle_errors
    def upload_video():
        """
        Upload video file and extract audio
        Returns unique ID for audio file retrieval
        """
        logger.info("Received video upload request")
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please provide a video file in the "file" field'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a video file to upload'
            }), 400
        
        # Validate file extension
        from config import Config
        if not Config.is_allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Allowed formats: {", ".join(Config.ALLOWED_VIDEO_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_video_path = os.path.join(tempfile.gettempdir(), f"upload_{os.urandom(8).hex()}_{filename}")
        
        try:
            # Save uploaded file
            file.save(temp_video_path)
            logger.info(f"Video file saved: {temp_video_path}")
            
            # Log memory usage before processing
            log_memory_usage()
            
            # Extract audio (this will delete the video file automatically)
            audio_path, error = audio_processor.extract_audio(temp_video_path, delete_video=True)
            
            if error:
                return jsonify({
                    'error': 'Audio extraction failed',
                    'message': error
                }), 500
            
            # Register audio file and get unique ID
            audio_id = file_manager.register_file(audio_path, 'audio')
            
            # Log memory usage after processing
            log_memory_usage()
            
            logger.info(f"Audio extraction completed successfully. ID: {audio_id}")
            
            return jsonify({
                'success': True,
                'audio_id': audio_id,
                'message': 'Audio extracted successfully'
            }), 200
            
        except Exception as e:
            # Clean up video file if still exists
            if os.path.exists(temp_video_path):
                from utils import safe_delete_file
                safe_delete_file(temp_video_path)
            
            logger.error(f"Error processing upload: {str(e)}")
            return jsonify({
                'error': 'Processing failed',
                'message': str(e)
            }), 500
    
    @app.route('/audio/<audio_id>', methods=['GET'])
    @handle_errors
    def get_audio(audio_id):
        """
        Retrieve audio file by ID and delete after serving
        """
        logger.info(f"Audio download request for ID: {audio_id}")
        
        # Get audio file path
        audio_path = file_manager.get_file_path(audio_id)
        
        if not audio_path:
            return jsonify({
                'error': 'Audio not found',
                'message': 'Invalid audio ID or file has expired'
            }), 404
        
        # Prepare file for download
        try:
            # Get filename for download
            filename = os.path.basename(audio_path)
            
            @after_this_request
            def cleanup_audio(response):
                """Delete audio file after successful response"""
                try:
                    if response.status_code == 200:
                        file_manager.delete_file(audio_id)
                        logger.info(f"Audio file deleted after serving: {audio_id}")
                    return response
                except Exception as e:
                    logger.error(f"Error in cleanup: {str(e)}")
                    return response
            
            # Send file
            return send_file(
                audio_path,
                as_attachment=True,
                download_name=filename,
                mimetype='audio/mpeg'
            )
            
        except Exception as e:
            logger.error(f"Error serving audio file: {str(e)}")
            return jsonify({
                'error': 'File serving failed',
                'message': str(e)
            }), 500
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get service statistics"""
        from config import Config
        stats = file_manager.get_stats()
        memory_mb = log_memory_usage()

        return jsonify({
            'file_manager': stats,
            'memory_mb': memory_mb,
            'config': {
                'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024),
                'allowed_formats': list(Config.ALLOWED_VIDEO_EXTENSIONS),
                'audio_format': Config.AUDIO_FORMAT
            }
        })
    
    # Cleanup on app shutdown
    @app.teardown_appcontext
    def cleanup_on_shutdown(error):
        if error:
            logger.error(f"Application error: {error}")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Development server
    config_obj = config[os.getenv('FLASK_ENV', 'default')]
    app.run(
        host=config_obj.HOST,
        port=config_obj.PORT,
        debug=config_obj.DEBUG
    )
