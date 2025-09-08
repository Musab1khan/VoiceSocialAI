import os
import logging
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.gemini_service import gemini_service

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send']

class EmailService:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.initialize_gmail_service()
    
    def initialize_gmail_service(self):
        """Initialize Gmail API service"""
        try:
            creds = None
            # Load existing credentials
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # This would need proper OAuth setup in production
                    logging.warning("Gmail credentials not found. Auto-reply will be disabled.")
                    return
            
            self.credentials = creds
            self.service = build('gmail', 'v1', credentials=creds)
            logging.info("Gmail service initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing Gmail service: {e}")
    
    def get_unread_emails(self, max_results=10):
        """Get unread emails"""
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me', 
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id']
                ).execute()
                
                # Extract email details
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Get email body
                body = self.extract_email_body(msg['payload'])
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'snippet': msg.get('snippet', '')
                })
            
            return emails
            
        except HttpError as e:
            logging.error(f"Error fetching emails: {e}")
            return []
    
    def extract_email_body(self, payload):
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_reply(self, original_email_id, reply_content):
        """Send reply to an email"""
        if not self.service:
            return False, "Gmail service not available"
        
        try:
            # Get original email for reply headers
            original = self.service.users().messages().get(
                userId='me', 
                id=original_email_id
            ).execute()
            
            headers = original['payload'].get('headers', [])
            original_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            original_from = next((h['value'] for h in headers if h['name'] == 'From'), '')
            original_message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')
            
            # Extract email address from "Name <email@domain.com>" format
            import re
            email_match = re.search(r'<(.+?)>', original_from)
            to_email = email_match.group(1) if email_match else original_from
            
            # Create reply message
            reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
            
            message = MIMEText(reply_content)
            message['to'] = to_email
            message['subject'] = reply_subject
            message['In-Reply-To'] = original_message_id
            message['References'] = original_message_id
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send reply
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            # Mark original as read
            self.service.users().messages().modify(
                userId='me',
                id=original_email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logging.info(f"Reply sent to {to_email}")
            return True, "Reply sent successfully"
            
        except Exception as e:
            logging.error(f"Error sending reply: {e}")
            return False, f"Error: {str(e)}"
    
    def process_auto_replies(self):
        """Process unread emails and send auto-replies"""
        if not self.service:
            logging.warning("Gmail service not available for auto-replies")
            return []
        
        processed = []
        
        try:
            unread_emails = self.get_unread_emails()
            
            for email in unread_emails:
                # Generate auto-reply using Gemini
                reply_content = gemini_service.generate_auto_reply(
                    email['body'] or email['snippet'],
                    context="email"
                )
                
                # Send reply
                success, message = self.send_reply(email['id'], reply_content)
                
                if success:
                    processed.append({
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'reply': reply_content,
                        'status': 'sent'
                    })
                    
                    # Log to database
                    from app import db
                    from models import AutoReplyLog
                    
                    log = AutoReplyLog(
                        platform='email',
                        sender=email['sender'],
                        original_message=email['body'] or email['snippet'],
                        reply_message=reply_content,
                        status='sent'
                    )
                    db.session.add(log)
                    db.session.commit()
                else:
                    processed.append({
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'error': message,
                        'status': 'failed'
                    })
            
            return processed
            
        except Exception as e:
            logging.error(f"Error processing auto-replies: {e}")
            return []

# Global email service instance
email_service = EmailService()
