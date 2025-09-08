import pyttsx3
import logging
from threading import Thread

class VoiceService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice()
        
    def setup_voice(self):
        """Configure voice settings"""
        try:
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to use a female voice if available
                for voice in voices:
                    if hasattr(voice, 'name') and voice.name and ('female' in voice.name.lower() or 'zira' in voice.name.lower()):
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    if hasattr(voices[0], 'id'):
                        self.engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 180)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
        except Exception as e:
            logging.error(f"Error setting up voice: {e}")
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            def _speak():
                self.engine.say(text)
                self.engine.runAndWait()
            
            # Run speech in separate thread to avoid blocking
            thread = Thread(target=_speak)
            thread.daemon = True
            thread.start()
            
            logging.info(f"Speaking: {text}")
            return True
            
        except Exception as e:
            logging.error(f"Error in text-to-speech: {e}")
            return False
    
    def get_voice_info(self):
        """Get current voice information"""
        try:
            voices = self.engine.getProperty('voices')
            current_voice = self.engine.getProperty('voice')
            rate = self.engine.getProperty('rate')
            volume = self.engine.getProperty('volume')
            
            available_voices = []
            if voices and len(voices) > 0:
                for v in voices:
                    if hasattr(v, 'id') and hasattr(v, 'name'):
                        available_voices.append({'id': v.id, 'name': v.name})
            
            return {
                'current_voice': current_voice,
                'available_voices': available_voices,
                'rate': rate,
                'volume': volume
            }
        except Exception as e:
            logging.error(f"Error getting voice info: {e}")
            return {}

# Global voice service instance
voice_service = VoiceService()
