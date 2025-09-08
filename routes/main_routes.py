from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main chat interface page"""
    return render_template('chat_home.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with command history and system status"""
    try:
        from models import CommandHistory, AutoReplyLog, SocialMediaPost
        
        # Get recent activities
        recent_commands = CommandHistory.query.order_by(CommandHistory.created_at.desc()).limit(10).all()
        recent_replies = AutoReplyLog.query.order_by(AutoReplyLog.created_at.desc()).limit(10).all()
        recent_posts = SocialMediaPost.query.order_by(SocialMediaPost.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             commands=recent_commands,
                             replies=recent_replies,
                             posts=recent_posts)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             commands=[], replies=[], posts=[],
                             error="Error loading dashboard data")

@main_bp.route('/text-generator')
def text_generator():
    """Text AI Generator page"""
    return render_template('text_generator.html')

@main_bp.route('/settings')
def settings():
    """Settings page for configuration"""
    try:
        from services.voice_service import voice_service
        import os
        
        voice_info = voice_service.get_voice_info()
        
        # Get current API key status (masked for security)
        api_keys = {
            # AI Text/Chat APIs
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
            'HUGGINGFACE_API_KEY': os.getenv('HUGGINGFACE_API_KEY'),
            'AIML_API_KEY': os.getenv('AIML_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            
            # Image Generation APIs
            'DEEPAI_API_KEY': os.getenv('DEEPAI_API_KEY'),
            'REPLICATE_API_KEY': os.getenv('REPLICATE_API_KEY'),
            'STABILITY_API_KEY': os.getenv('STABILITY_API_KEY'),
            
            # TTS/Voice APIs
            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
            'ASSEMBLY_API_KEY': os.getenv('ASSEMBLY_API_KEY'),
            
            # Social Media APIs
            'FACEBOOK_ACCESS_TOKEN': os.getenv('FACEBOOK_ACCESS_TOKEN'),
            'FACEBOOK_PAGE_ID': os.getenv('FACEBOOK_PAGE_ID'),
            
            # Communication APIs
            'GMAIL_CLIENT_ID': os.getenv('GMAIL_CLIENT_ID'),
            'GMAIL_CLIENT_SECRET': os.getenv('GMAIL_CLIENT_SECRET'),
            'WHATSAPP_TOKEN': os.getenv('WHATSAPP_TOKEN'),
            'WHATSAPP_VERIFY_TOKEN': os.getenv('WHATSAPP_VERIFY_TOKEN')
        }
        
        return render_template('settings.html', voice_info=voice_info, api_keys=api_keys)
    except Exception as e:
        logging.error(f"Error loading settings: {e}")
        return render_template('settings.html', voice_info={}, api_keys={}, error="Error loading settings")

@main_bp.route('/test-voice')
def test_voice():
    """Test voice functionality"""
    try:
        from services.voice_service import voice_service
        voice_service.speak("Voice test successful. I can speak clearly.")
        return jsonify({'success': True, 'message': 'Voice test completed'})
    except Exception as e:
        logging.error(f"Error in voice test: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/whatsapp-webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """WhatsApp webhook endpoint"""
    try:
        from services.whatsapp_service import whatsapp_service
        
        if request.method == 'GET':
            # Webhook verification
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            result = whatsapp_service.verify_webhook(mode, token, challenge)
            if result:
                return result
            else:
                return 'Verification failed', 403
        
        elif request.method == 'POST':
            # Process incoming message
            message_data = request.get_json()
            success = whatsapp_service.process_incoming_message(message_data)
            
            if success:
                return 'OK', 200
            else:
                return 'Error processing message', 500
                
    except Exception as e:
        logging.error(f"Error in WhatsApp webhook: {e}")
        return 'Internal server error', 500
