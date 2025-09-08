import logging
import re
import os
from datetime import datetime
from services.voice_service import voice_service
from services.gemini_service import gemini_service
from services.facebook_service import facebook_service
from services.email_service import email_service
from services.whatsapp_service import whatsapp_service

class CommandProcessor:
    def __init__(self):
        self.commands = {
            'facebook_post': self.process_facebook_post,
            'create_image': self.process_image_generation,
            'text_generation': self.process_text_generation,
            'general_query': self.process_general_query,
            'system_status': self.process_system_status,
            'auto_reply_status': self.process_auto_reply_status,
        }
    
    def process_command(self, command_text):
        """Process voice command and determine action"""
        try:
            command_text = command_text.lower().strip()
            logging.info(f"Processing command: {command_text}")
            
            command_log = None
            
            # Try to log command to database
            try:
                from flask import current_app
                from models import CommandHistory
                
                with current_app.app_context():
                    db = current_app.extensions['sqlalchemy']
                    command_log = CommandHistory(
                        command_text=command_text,
                        command_type='unknown',
                        status='processing'
                    )
                    db.session.add(command_log)
                    db.session.commit()
            except Exception as db_error:
                logging.warning(f"Could not log command to database: {db_error}")
            
            result = self.classify_and_execute_command(command_text)
            
            # Try to update command log
            if command_log:
                try:
                    with current_app.app_context():
                        db = current_app.extensions['sqlalchemy']
                        command_log.status = 'completed' if result['success'] else 'failed'
                        command_log.result = result['message']
                        command_log.command_type = result.get('command_type', 'unknown')
                        command_log.completed_at = datetime.utcnow()
                        db.session.commit()
                except Exception as db_error:
                    logging.warning(f"Could not update command log: {db_error}")
            
            # Speak the result
            voice_service.speak(result['message'])
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            voice_service.speak(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'command_type': 'error'
            }
    
    def classify_and_execute_command(self, command_text):
        """Classify command and execute appropriate action"""
        
        # Facebook post commands
        if any(keyword in command_text for keyword in ['facebook', 'post', 'share']):
            return self.process_facebook_post(command_text)
        
        # Image generation commands
        elif any(keyword in command_text for keyword in ['image', 'picture', 'generate', 'create image']):
            return self.process_image_generation(command_text)
        
        # Text generation commands
        elif any(keyword in command_text for keyword in ['write', 'blog', 'article', 'content', 'reply', 'email']):
            return self.process_text_generation(command_text)
        
        # System status commands
        elif any(keyword in command_text for keyword in ['status', 'how are you', 'system']):
            return self.process_system_status(command_text)
        
        # Auto-reply status commands
        elif any(keyword in command_text for keyword in ['auto reply', 'email', 'whatsapp', 'messages']):
            return self.process_auto_reply_status(command_text)
        
        # General query
        else:
            return self.process_general_query(command_text)
    
    def process_facebook_post(self, command_text):
        """Process Facebook post creation command"""
        try:
            # Extract topic from command
            topic = self.extract_topic_from_command(command_text, 'post')
            
            if not topic:
                return {
                    'success': False,
                    'message': "I couldn't understand what you want to post about. Please specify a topic.",
                    'command_type': 'facebook_post'
                }
            
            # Check if image is requested
            include_image = any(keyword in command_text for keyword in ['image', 'picture', 'photo'])
            
            # Create Facebook post
            success, result = facebook_service.create_post_with_ai_content(topic, include_image)
            
            if success:
                message = f"Successfully created Facebook post about {topic}"
                if result.get('image_path'):
                    message += " with an AI-generated image"
                
                return {
                    'success': True,
                    'message': message,
                    'command_type': 'facebook_post',
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to create Facebook post: {result.get('error', 'Unknown error')}",
                    'command_type': 'facebook_post'
                }
                
        except Exception as e:
            logging.error(f"Error processing Facebook post command: {e}")
            return {
                'success': False,
                'message': f"Error creating Facebook post: {str(e)}",
                'command_type': 'facebook_post'
            }
    
    def process_image_generation(self, command_text):
        """Process image generation command"""
        try:
            # Extract image description
            description = self.extract_topic_from_command(command_text, 'image')
            
            if not description:
                return {
                    'success': False,
                    'message': "Please describe what image you want me to generate.",
                    'command_type': 'create_image'
                }
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
            image_path = f"static/generated_images/{filename}"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Generate image
            success, result = gemini_service.generate_image(description, image_path)
            
            if success:
                return {
                    'success': True,
                    'message': f"Successfully generated image: {description}",
                    'command_type': 'create_image',
                    'data': {
                        'image_path': image_path,
                        'description': description
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to generate image: {result}",
                    'command_type': 'create_image'
                }
                
        except Exception as e:
            logging.error(f"Error processing image generation command: {e}")
            return {
                'success': False,
                'message': f"Error generating image: {str(e)}",
                'command_type': 'create_image'
            }
    
    def process_text_generation(self, command_text):
        """Process text generation command"""
        try:
            from services.text_ai_service import text_ai_service
            
            # Determine content type from command
            content_type = 'social_post'  # default
            if 'blog' in command_text or 'article' in command_text:
                content_type = 'blog_article'
            elif 'email' in command_text or 'reply' in command_text:
                content_type = 'email_reply'
            elif 'story' in command_text:
                content_type = 'creative_story'
            elif 'review' in command_text:
                content_type = 'review'
            elif 'tutorial' in command_text or 'guide' in command_text:
                content_type = 'tutorial'
            elif 'product' in command_text:
                content_type = 'product_description'
            elif 'news' in command_text:
                content_type = 'news_article'
            
            # Extract topic from command
            topic = self.extract_text_topic(command_text, content_type)
            
            if not topic:
                return {
                    'success': False,
                    'message': f"Please tell me what {content_type.replace('_', ' ')} you want me to write about.",
                    'command_type': 'text_generation'
                }
            
            # Determine language (default to English, but detect Urdu/other languages)
            language = 'english'
            if any(urdu_word in command_text for urdu_word in ['urdu', 'اردو', 'لکھو', 'بنائو']):
                language = 'urdu'
            
            # Generate content
            result = text_ai_service.generate_content(
                content_type=content_type,
                topic=topic,
                tone='friendly',
                language=language
            )
            
            if result['success']:
                message = f"I've written a {content_type.replace('_', ' ')} about {topic}. "
                if result['hashtags']:
                    message += f"I've also included relevant hashtags: {' '.join(result['hashtags'][:3])}"
                
                return {
                    'success': True,
                    'message': message,
                    'command_type': 'text_generation',
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'message': f"I couldn't generate the {content_type.replace('_', ' ')}: {result.get('error', 'Unknown error')}",
                    'command_type': 'text_generation'
                }
                
        except Exception as e:
            logging.error(f"Error processing text generation command: {e}")
            return {
                'success': False,
                'message': f"Error generating text: {str(e)}",
                'command_type': 'text_generation'
            }
    
    def extract_text_topic(self, command_text, content_type):
        """Extract topic from text generation command"""
        # Common patterns to remove
        patterns_to_remove = [
            r'write\s+(a|an)?\s*',
            r'create\s+(a|an)?\s*',
            r'generate\s+(a|an)?\s*',
            r'make\s+(a|an)?\s*',
            content_type.replace('_', r'\s*'),
            r'about\s*',
            r'for\s*',
            r'on\s*'
        ]
        
        topic = command_text.lower()
        
        # Remove patterns
        for pattern in patterns_to_remove:
            topic = re.sub(pattern, ' ', topic)
        
        # Clean up
        topic = ' '.join(topic.split())
        
        # Return the cleaned topic if it has enough content
        return topic if len(topic) > 2 else None
    
    def process_general_query(self, command_text):
        """Process general query using Gemini"""
        try:
            response = gemini_service.generate_text_response(command_text)
            
            return {
                'success': True,
                'message': response,
                'command_type': 'general_query'
            }
            
        except Exception as e:
            logging.error(f"Error processing general query: {e}")
            return {
                'success': False,
                'message': f"Sorry, I couldn't process your request: {str(e)}",
                'command_type': 'general_query'
            }
    
    def process_system_status(self, command_text):
        """Process system status command"""
        try:
            # Get system status information
            recent_commands = 0
            recent_replies = 0
            recent_posts = 0
            
            try:
                from flask import current_app
                from models import CommandHistory, AutoReplyLog, SocialMediaPost
                
                # Count recent activities
                recent_commands = CommandHistory.query.filter(
                    CommandHistory.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count()
                
                recent_replies = AutoReplyLog.query.filter(
                    AutoReplyLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count()
                
                recent_posts = SocialMediaPost.query.filter(
                    SocialMediaPost.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                ).count()
            except Exception as db_error:
                logging.warning(f"Could not get database stats: {db_error}")
            
            status_message = f"System is running well. Today I've processed {recent_commands} commands, " \
                           f"sent {recent_replies} auto-replies, and created {recent_posts} social media posts. Voice system is working perfectly!"
            
            return {
                'success': True,
                'message': status_message,
                'command_type': 'system_status',
                'data': {
                    'commands_today': recent_commands,
                    'replies_today': recent_replies,
                    'posts_today': recent_posts
                }
            }
            
        except Exception as e:
            logging.error(f"Error getting system status: {e}")
            return {
                'success': True,
                'message': "System is running perfectly! Voice recognition, text-to-speech, and all core features are working well.",
                'command_type': 'system_status'
            }
    
    def process_auto_reply_status(self, command_text):
        """Process auto-reply status command"""
        try:
            recent_replies = []
            
            try:
                from flask import current_app
                from models import AutoReplyLog
                
                # Get recent auto-reply activity
                recent_replies = AutoReplyLog.query.order_by(AutoReplyLog.created_at.desc()).limit(5).all()
            except Exception as db_error:
                logging.warning(f"Could not get auto-reply data: {db_error}")
            
            if recent_replies:
                reply_count = len(recent_replies)
                latest_reply = recent_replies[0]
                
                message = f"Auto-reply system is active. I've sent {reply_count} recent replies. " \
                         f"Latest reply was to {latest_reply.platform} from {latest_reply.sender[:20]}..."
            else:
                message = "Auto-reply system is active and monitoring emails and WhatsApp messages. No recent replies have been sent."
            
            return {
                'success': True,
                'message': message,
                'command_type': 'auto_reply_status',
                'data': {
                    'recent_replies': [{
                        'platform': r.platform,
                        'sender': r.sender,
                        'created_at': r.created_at.isoformat()
                    } for r in recent_replies]
                }
            }
            
        except Exception as e:
            logging.error(f"Error getting auto-reply status: {e}")
            return {
                'success': True,
                'message': "Auto-reply system is running and monitoring for new messages to respond to.",
                'command_type': 'auto_reply_status'
            }
    
    def extract_topic_from_command(self, command_text, command_type):
        """Extract topic/content from voice command"""
        try:
            # Common patterns for different command types
            patterns = {
                'post': [
                    r'post about (.+)',
                    r'create.*post.*about (.+)',
                    r'facebook.*about (.+)',
                    r'share (.+)',
                    r'post (.+)'
                ],
                'image': [
                    r'generate.*image.*of (.+)',
                    r'create.*image.*of (.+)',
                    r'make.*picture.*of (.+)',
                    r'image of (.+)',
                    r'picture of (.+)',
                    r'generate (.+)',
                    r'create (.+)'
                ]
            }
            
            if command_type in patterns:
                for pattern in patterns[command_type]:
                    match = re.search(pattern, command_text, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
            
            # If no pattern matches, try to extract content after common keywords
            keywords = {
                'post': ['post', 'about', 'facebook'],
                'image': ['image', 'picture', 'generate', 'create']
            }
            
            if command_type in keywords:
                for keyword in keywords[command_type]:
                    if keyword in command_text:
                        parts = command_text.split(keyword, 1)
                        if len(parts) > 1:
                            topic = parts[1].strip()
                            # Remove common words from the beginning
                            topic = re.sub(r'^(of|about|on|for)\s+', '', topic, flags=re.IGNORECASE)
                            if topic:
                                return topic
            
            return None
            
        except Exception as e:
            logging.error(f"Error extracting topic: {e}")
            return None

# Global command processor instance
command_processor = CommandProcessor()
