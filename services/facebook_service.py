import os
import logging
import requests
from services.gemini_service import gemini_service

class FacebookService:
    def __init__(self):
        self.access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN", "default_facebook_token")
        self.page_id = os.environ.get("FACEBOOK_PAGE_ID", "default_page_id")
        self.base_url = "https://graph.facebook.com/v17.0"
    
    def create_text_post(self, message):
        """Create a text post on Facebook"""
        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            
            params = {
                'message': message,
                'access_token': self.access_token
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                
                logging.info(f"Facebook post created with ID: {post_id}")
                return True, post_id, "Post created successfully"
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logging.error(f"Failed to create Facebook post: {error_msg}")
                return False, None, f"Error: {error_msg}"
                
        except Exception as e:
            logging.error(f"Error creating Facebook post: {e}")
            return False, None, f"Error: {str(e)}"
    
    def create_photo_post(self, message, photo_path):
        """Create a photo post on Facebook"""
        try:
            url = f"{self.base_url}/{self.page_id}/photos"
            
            with open(photo_path, 'rb') as photo_file:
                files = {'source': photo_file}
                data = {
                    'message': message,
                    'access_token': self.access_token
                }
                
                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                
                logging.info(f"Facebook photo post created with ID: {post_id}")
                return True, post_id, "Photo post created successfully"
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logging.error(f"Failed to create Facebook photo post: {error_msg}")
                return False, None, f"Error: {error_msg}"
                
        except Exception as e:
            logging.error(f"Error creating Facebook photo post: {e}")
            return False, None, f"Error: {str(e)}"
    
    def create_post_with_ai_content(self, topic, include_image=False):
        """Create Facebook post with AI-generated content and optional image"""
        try:
            # Generate post content using Gemini
            post_content = gemini_service.generate_facebook_post(topic)
            
            post_id = None
            image_path = None
            
            if include_image:
                # Generate image
                image_path = f"static/generated_images/facebook_post_{topic.replace(' ', '_')}.png"
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                success, image_result = gemini_service.generate_image(
                    f"Create an image for Facebook post about: {topic}",
                    image_path
                )
                
                if success:
                    success, post_id, message = self.create_photo_post(post_content, image_path)
                else:
                    logging.warning(f"Image generation failed: {image_result}")
                    success, post_id, message = self.create_text_post(post_content)
            else:
                success, post_id, message = self.create_text_post(post_content)
            
            if success:
                # Log to database
                from app import db
                from models import SocialMediaPost
                
                post = SocialMediaPost(
                    platform='facebook',
                    content=post_content,
                    image_path=image_path,
                    post_id=post_id,
                    status='posted'
                )
                db.session.add(post)
                db.session.commit()
                
                return True, {
                    'post_id': post_id,
                    'content': post_content,
                    'image_path': image_path,
                    'message': message
                }
            else:
                return False, {'error': message}
                
        except Exception as e:
            logging.error(f"Error creating AI Facebook post: {e}")
            return False, {'error': f"Error: {str(e)}"}
    
    def get_recent_posts(self, limit=10):
        """Get recent Facebook posts"""
        try:
            url = f"{self.base_url}/{self.page_id}/posts"
            
            params = {
                'access_token': self.access_token,
                'limit': limit,
                'fields': 'id,message,created_time,story'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return True, result.get('data', [])
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logging.error(f"Failed to get Facebook posts: {error_msg}")
                return False, f"Error: {error_msg}"
                
        except Exception as e:
            logging.error(f"Error getting Facebook posts: {e}")
            return False, f"Error: {str(e)}"
    
    def delete_post(self, post_id):
        """Delete a Facebook post"""
        try:
            url = f"{self.base_url}/{post_id}"
            
            params = {
                'access_token': self.access_token
            }
            
            response = requests.delete(url, params=params)
            
            if response.status_code == 200:
                logging.info(f"Facebook post {post_id} deleted")
                return True, "Post deleted successfully"
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logging.error(f"Failed to delete Facebook post: {error_msg}")
                return False, f"Error: {error_msg}"
                
        except Exception as e:
            logging.error(f"Error deleting Facebook post: {e}")
            return False, f"Error: {str(e)}"

# Global Facebook service instance
facebook_service = FacebookService()
