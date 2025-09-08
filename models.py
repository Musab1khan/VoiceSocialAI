from app import db
from datetime import datetime
from sqlalchemy import Text

class CommandHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_text = db.Column(Text, nullable=False)
    command_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')
    result = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __init__(self, command_text, command_type, status='pending', result=None):
        self.command_text = command_text
        self.command_type = command_type
        self.status = status
        self.result = result

class AutoReplyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # email, whatsapp
    sender = db.Column(db.String(255), nullable=False)
    original_message = db.Column(Text, nullable=False)
    reply_message = db.Column(Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='sent')
    
    def __init__(self, platform, sender, original_message, reply_message, status='sent'):
        self.platform = platform
        self.sender = sender
        self.original_message = original_message
        self.reply_message = reply_message
        self.status = status

class SocialMediaPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # facebook
    content = db.Column(Text, nullable=False)
    image_path = db.Column(db.String(255))
    post_id = db.Column(db.String(255))
    status = db.Column(db.String(20), default='posted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, platform, content, image_path=None, post_id=None, status='posted'):
        self.platform = platform
        self.content = content
        self.image_path = image_path
        self.post_id = post_id
        self.status = status

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
