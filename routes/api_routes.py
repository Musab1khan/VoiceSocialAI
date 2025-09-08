from flask import Blueprint, request, jsonify, send_file
import logging
import os
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/process-command', methods=['POST'])
def process_command():
    """Process voice command"""
    try:
        data = request.get_json()
        command_text = data.get('command', '').strip()
        
        if not command_text:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400
        
        from services.command_processor import command_processor
        result = command_processor.process_command(command_text)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error processing command API: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@api_bp.route('/voice-test', methods=['POST'])
def voice_test():
    """Test voice output"""
    try:
        data = request.get_json()
        text = data.get('text', 'This is a voice test')
        
        from services.voice_service import voice_service
        success = voice_service.speak(text)
        
        return jsonify({
            'success': success,
            'message': 'Voice test completed' if success else 'Voice test failed'
        })
        
    except Exception as e:
        logging.error(f"Error in voice test API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/system-status', methods=['GET'])
def system_status():
    """Get system status"""
    try:
        from models import CommandHistory, AutoReplyLog, SocialMediaPost
        
        # Get today's statistics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0)
        
        commands_today = CommandHistory.query.filter(CommandHistory.created_at >= today).count()
        replies_today = AutoReplyLog.query.filter(AutoReplyLog.created_at >= today).count()
        posts_today = SocialMediaPost.query.filter(SocialMediaPost.created_at >= today).count()
        
        # Get recent activities
        recent_commands = CommandHistory.query.order_by(CommandHistory.created_at.desc()).limit(5).all()
        recent_replies = AutoReplyLog.query.order_by(AutoReplyLog.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'status': {
                'commands_today': commands_today,
                'replies_today': replies_today,
                'posts_today': posts_today,
                'recent_commands': [{
                    'id': cmd.id,
                    'command_text': cmd.command_text,
                    'command_type': cmd.command_type,
                    'status': cmd.status,
                    'created_at': cmd.created_at.isoformat()
                } for cmd in recent_commands],
                'recent_replies': [{
                    'id': reply.id,
                    'platform': reply.platform,
                    'sender': reply.sender,
                    'status': reply.status,
                    'created_at': reply.created_at.isoformat()
                } for reply in recent_replies]
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting system status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/manual-auto-reply', methods=['POST'])
def manual_auto_reply():
    """Manually trigger auto-reply processing"""
    try:
        from services.email_service import email_service
        
        # Process email auto-replies
        processed_emails = email_service.process_auto_replies()
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(processed_emails)} emails',
            'processed_emails': processed_emails
        })
        
    except Exception as e:
        logging.error(f"Error in manual auto-reply: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/create-facebook-post', methods=['POST'])
def create_facebook_post():
    """Create Facebook post via API"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        include_image = data.get('include_image', False)
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        from services.facebook_service import facebook_service
        success, result = facebook_service.create_post_with_ai_content(topic, include_image)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Facebook post created successfully',
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logging.error(f"Error creating Facebook post: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/generate-image', methods=['POST'])
def generate_image():
    """Generate image via API"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_generated_{timestamp}.png"
        image_path = f"static/generated_images/{filename}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        from services.gemini_service import gemini_service
        success, result = gemini_service.generate_image(prompt, image_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Image generated successfully',
                'image_path': image_path,
                'image_url': f'/{image_path}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 500
            
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/command-history', methods=['GET'])
def command_history():
    """Get command history"""
    try:
        from models import CommandHistory
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        commands = CommandHistory.query.order_by(CommandHistory.created_at.desc())\
                                      .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'commands': [{
                'id': cmd.id,
                'command_text': cmd.command_text,
                'command_type': cmd.command_type,
                'status': cmd.status,
                'result': cmd.result,
                'created_at': cmd.created_at.isoformat(),
                'completed_at': cmd.completed_at.isoformat() if cmd.completed_at else None
            } for cmd in commands.items],
            'pagination': {
                'page': commands.page,
                'pages': commands.pages,
                'per_page': commands.per_page,
                'total': commands.total
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting command history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/download-image/<path:filename>')
def download_image(filename):
    """Download generated image"""
    try:
        image_path = f"static/generated_images/{filename}"
        
        if os.path.exists(image_path):
            return send_file(image_path, as_attachment=True)
        else:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
            
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/generate-text', methods=['POST'])
def generate_text():
    """Generate text content using AI"""
    try:
        from services.text_ai_service import text_ai_service
        
        data = request.get_json()
        content_type = data.get('content_type', 'social_post')
        topic = data.get('topic', '').strip()
        tone = data.get('tone', 'friendly')
        language = data.get('language', 'english')
        custom_instructions = data.get('custom_instructions', '')
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Generate content
        result = text_ai_service.generate_content(
            content_type=content_type,
            topic=topic,
            tone=tone,
            language=language,
            custom_instructions=custom_instructions
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error generating text: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/content-types', methods=['GET'])
def get_content_types():
    """Get available content types"""
    try:
        from services.text_ai_service import text_ai_service
        
        content_types = text_ai_service.get_available_content_types()
        return jsonify({
            'success': True,
            'content_types': content_types
        })
        
    except Exception as e:
        logging.error(f"Error getting content types: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/ai-provider-status', methods=['GET'])
def get_ai_provider_status():
    """Get AI provider availability status"""
    try:
        from services.text_ai_service import text_ai_service
        
        status = text_ai_service.get_provider_status()
        return jsonify({
            'success': True,
            'providers': status
        })
        
    except Exception as e:
        logging.error(f"Error getting provider status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/chat-message', methods=['POST'])
def chat_message():
    """Handle chat messages with file attachments and camera captures"""
    try:
        from services.text_ai_service import text_ai_service
        from services.file_processor import file_processor
        from langdetect import detect
        
        message = request.form.get('message', '').strip()
        attachments_info = request.form.get('attachments', '[]')
        camera_capture = request.form.get('camera_capture')
        
        # Parse attachments info
        try:
            attachments_info = json.loads(attachments_info)
        except:
            attachments_info = []
        
        processed_attachments = []
        file_contents = []
        
        # Process uploaded files
        for i, attachment_info in enumerate(attachments_info):
            file_key = f'file_{i}'
            if file_key in request.files:
                uploaded_file = request.files[file_key]
                if uploaded_file.filename:
                    try:
                        file_data = uploaded_file.read()
                        result = file_processor.process_file(file_data, uploaded_file.filename)
                        
                        if result['success']:
                            processed_attachments.append({
                                'name': uploaded_file.filename,
                                'type': result['file_type'],
                                'size': result['file_size'],
                                'analysis': result['processed_data']
                            })
                            
                            # Add content to file_contents for AI processing
                            if 'content' in result['processed_data']:
                                file_contents.append({
                                    'filename': uploaded_file.filename,
                                    'content': result['processed_data']['content'],
                                    'type': result['file_type']
                                })
                        else:
                            processed_attachments.append({
                                'name': uploaded_file.filename,
                                'type': 'error',
                                'error': result.get('error', 'Unknown error')
                            })
                    except Exception as e:
                        logging.error(f"Error processing file {uploaded_file.filename}: {e}")
                        processed_attachments.append({
                            'name': uploaded_file.filename,
                            'type': 'error',
                            'error': str(e)
                        })
        
        # Process camera capture
        if camera_capture:
            try:
                result = file_processor.process_camera_capture(camera_capture)
                if result.get('success', False):
                    processed_attachments.append({
                        'name': 'Camera Capture',
                        'type': 'camera_image',
                        'analysis': result
                    })
                    file_contents.append({
                        'filename': 'camera_capture.jpg',
                        'content': f"Camera captured image analysis: {result.get('content', 'Image analyzed')}",
                        'type': 'image'
                    })
            except Exception as e:
                logging.error(f"Error processing camera capture: {e}")
        
        # Detect message language
        message_language = 'english'
        if message:
            try:
                detected_lang = detect(message)
                language_map = {
                    'en': 'english',
                    'ur': 'urdu',
                    'ar': 'arabic',
                    'hi': 'hindi',
                    'es': 'spanish',
                    'fr': 'french'
                }
                message_language = language_map.get(detected_lang, 'english')
            except:
                message_language = 'english'
        
        # Build comprehensive prompt for AI
        ai_prompt = ""
        
        if message:
            ai_prompt += f"User message: {message}\n\n"
        
        if file_contents:
            ai_prompt += "Attached files content:\n"
            for file_info in file_contents:
                ai_prompt += f"\n--- {file_info['filename']} ({file_info['type']}) ---\n"
                ai_prompt += file_info['content'][:2000]  # Limit content length
                if len(file_info['content']) > 2000:
                    ai_prompt += "\n[Content truncated...]"
                ai_prompt += "\n"
        
        if not ai_prompt.strip():
            ai_prompt = "User sent attachments without a message. Please analyze and respond to the attached content."
        
        # Add context about capabilities
        ai_prompt += f"\n\nPlease respond in {message_language}. You are an AI assistant with access to:"
        ai_prompt += "\n- File analysis (documents, images, spreadsheets, archives)"
        ai_prompt += "\n- Computer vision and OpenCV image processing"
        ai_prompt += "\n- Text generation and content creation"
        ai_prompt += "\n- Multi-language support"
        ai_prompt += "\nProvide helpful, accurate responses based on the user's input and any attached content."
        
        # Generate AI response
        ai_response = text_ai_service._use_gemini(ai_prompt, 1000)
        
        if not ai_response:
            # Fallback to other providers
            ai_response = text_ai_service._use_openai(ai_prompt, 1000)
            if not ai_response:
                ai_response = text_ai_service._use_huggingface(ai_prompt, 1000)
                if not ai_response:
                    ai_response = "I apologize, but I'm having trouble processing your request right now. Please try again or check your API keys in settings."
        
        # Prepare response attachments (analysis results, generated content, etc.)
        response_attachments = []
        
        # Add file analysis results as attachments
        for attachment in processed_attachments:
            if attachment.get('analysis'):
                response_attachments.append({
                    'type': 'analysis',
                    'name': f"Analysis: {attachment['name']}",
                    'content': attachment['analysis']
                })
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'language_detected': message_language,
            'processed_attachments': processed_attachments,
            'attachments': response_attachments,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error processing chat message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/generate-text-ai', methods=['POST'])
def generate_text_ai():
    """Generate AI content using the text AI service"""
    try:
        from services.text_ai_service import text_ai_service
        
        data = request.get_json()
        
        content_type = data.get('content_type', 'social_post')
        language = data.get('language', 'english')
        tone = data.get('tone', 'friendly')
        word_count = data.get('word_count', 200)
        add_hashtags = data.get('add_hashtags', False)
        seo_optimize = data.get('seo_optimize', False)
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Generate content using text AI service
        result = text_ai_service.generate_content(
            content_type=content_type,
            prompt=prompt,
            language=language,
            tone=tone,
            word_count=word_count,
            add_hashtags=add_hashtags,
            seo_optimize=seo_optimize
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'content': result['content'],
                'metadata': result.get('metadata', {}),
                'provider_used': result.get('provider_used', 'unknown')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate content')
            }), 500
            
    except Exception as e:
        logging.error(f"Error in generate_text_ai: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/update-config', methods=['POST'])
def update_config():
    """Update API configuration"""
    try:
        import os
        data = request.get_json()
        
        # Environment variable mappings
        env_mappings = {
            # AI Text/Chat APIs
            'gemini_api_key': 'GEMINI_API_KEY',
            'huggingface_api_key': 'HUGGINGFACE_API_KEY',
            'aiml_api_key': 'AIML_API_KEY',
            'openai_api_key': 'OPENAI_API_KEY',
            
            # Image Generation APIs
            'deepai_api_key': 'DEEPAI_API_KEY',
            'replicate_api_key': 'REPLICATE_API_KEY',
            'stability_api_key': 'STABILITY_API_KEY',
            
            # TTS/Voice APIs
            'elevenlabs_api_key': 'ELEVENLABS_API_KEY',
            'assembly_api_key': 'ASSEMBLY_API_KEY',
            
            # Social Media APIs
            'facebook_access_token': 'FACEBOOK_ACCESS_TOKEN',
            'facebook_page_id': 'FACEBOOK_PAGE_ID',
            
            # Communication APIs
            'gmail_client_id': 'GMAIL_CLIENT_ID',
            'gmail_client_secret': 'GMAIL_CLIENT_SECRET',
            'whatsapp_token': 'WHATSAPP_TOKEN',
            'whatsapp_verify_token': 'WHATSAPP_VERIFY_TOKEN'
        }
        
        updated_keys = []
        
        # Update environment variables
        for form_key, env_key in env_mappings.items():
            if form_key in data and data[form_key]:
                value = data[form_key]
                # Don't update if it's masked (showing asterisks)
                if not value.startswith('*'):
                    os.environ[env_key] = value
                    updated_keys.append(env_key)
        
        logging.info(f"Updated API keys: {updated_keys}")
        
        return jsonify({
            'success': True, 
            'message': f'Updated {len(updated_keys)} API keys successfully',
            'updated_keys': updated_keys
        })
        
    except Exception as e:
        logging.error(f"Error updating API configuration: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to update configuration: {str(e)}'
        }), 500
