import logging
from services.email_service import email_service
from services.whatsapp_service import whatsapp_service

def start_auto_reply_monitoring(scheduler):
    """Start background tasks for auto-reply monitoring"""
    
    # Schedule email monitoring every 5 minutes
    scheduler.add_job(
        func=monitor_emails,
        trigger="interval",
        minutes=5,
        id='email_monitor',
        name='Monitor emails for auto-reply',
        replace_existing=True
    )
    
    logging.info("Auto-reply monitoring started")

def monitor_emails():
    """Monitor and process email auto-replies"""
    try:
        logging.info("Running email auto-reply check...")
        processed = email_service.process_auto_replies()
        
        if processed:
            logging.info(f"Processed {len(processed)} email auto-replies")
        else:
            logging.debug("No emails to process")
            
    except Exception as e:
        logging.error(f"Error in email monitoring task: {e}")

def monitor_whatsapp():
    """Monitor WhatsApp messages (called via webhook)"""
    try:
        logging.info("Processing WhatsApp message...")
        # This function is called by webhook, not scheduled
        
    except Exception as e:
        logging.error(f"Error in WhatsApp monitoring: {e}")
