import os
import logging
import requests
from services.gemini_service import gemini_service

class WhatsAppService:
    def __init__(self):
        self.access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "default_whatsapp_token")
        self.phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "default_phone_id")
        self.verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "default_verify_token")
        self.base_url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
    
    def send_message(self, to_number, message_text):
        """Send WhatsApp message"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'text',
                'text': {
                    'body': message_text
                }
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logging.info(f"WhatsApp message sent to {to_number}")
                return True, "Message sent successfully"
            else:
                logging.error(f"Failed to send WhatsApp message: {response.text}")
                return False, f"Error: {response.text}"
                
        except Exception as e:
            logging.error(f"Error sending WhatsApp message: {e}")
            return False, f"Error: {str(e)}"
    
    def send_auto_reply(self, to_number, original_message):
        """Send auto-reply to WhatsApp message"""
        try:
            # Generate auto-reply using Gemini
            reply_content = gemini_service.generate_auto_reply(
                original_message,
                context="whatsapp"
            )
            
            success, message = self.send_message(to_number, reply_content)
            
            if success:
                # Log to database
                from app import db
                from models import AutoReplyLog
                
                log = AutoReplyLog(
                    platform='whatsapp',
                    sender=to_number,
                    original_message=original_message,
                    reply_message=reply_content,
                    status='sent'
                )
                db.session.add(log)
                db.session.commit()
                
                return True, reply_content
            else:
                return False, message
                
        except Exception as e:
            logging.error(f"Error sending WhatsApp auto-reply: {e}")
            return False, f"Error: {str(e)}"
    
    def process_incoming_message(self, message_data):
        """Process incoming WhatsApp message"""
        try:
            # Extract message details
            if 'messages' in message_data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}):
                messages = message_data['entry'][0]['changes'][0]['value']['messages']
                
                for message in messages:
                    from_number = message['from']
                    message_text = message.get('text', {}).get('body', '')
                    
                    if message_text:
                        # Send auto-reply
                        success, reply = self.send_auto_reply(from_number, message_text)
                        
                        if success:
                            logging.info(f"Auto-reply sent to {from_number}: {reply}")
                        else:
                            logging.error(f"Failed to send auto-reply to {from_number}: {reply}")
                
                return True
                
        except Exception as e:
            logging.error(f"Error processing WhatsApp message: {e}")
            return False
    
    def verify_webhook(self, mode, token, challenge):
        """Verify WhatsApp webhook"""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def get_recent_messages(self, limit=10):
        """Get recent WhatsApp conversations (if supported by API)"""
        # Note: WhatsApp Business API doesn't provide message history retrieval
        # This would need to be implemented with a local message store
        try:
            from app import db
            from models import AutoReplyLog
            
            recent_replies = AutoReplyLog.query.filter_by(platform='whatsapp')\
                                             .order_by(AutoReplyLog.created_at.desc())\
                                             .limit(limit).all()
            
            return [{
                'sender': log.sender,
                'original_message': log.original_message,
                'reply_message': log.reply_message,
                'created_at': log.created_at.isoformat(),
                'status': log.status
            } for log in recent_replies]
            
        except Exception as e:
            logging.error(f"Error getting recent messages: {e}")
            return []

# Global WhatsApp service instance
whatsapp_service = WhatsAppService()
