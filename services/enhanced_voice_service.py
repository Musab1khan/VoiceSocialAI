"""
Enhanced Voice Service with multilingual support
Supports Urdu, Pashto, English and other languages
"""

import pyttsx3
import logging
import os
from threading import Thread
from typing import Dict, Optional, List

class EnhancedVoiceService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.current_language = 'en'
        self.language_voices = {}
        self.setup_voice()
        self._discover_language_voices()
        
    def setup_voice(self):
        """Configure voice settings"""
        try:
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to find best voice for current language
                self._set_language_voice(self.current_language)
            
            # Set speech properties
            self.engine.setProperty('rate', 180)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
        except Exception as e:
            logging.error(f"Error setting up voice: {e}")
    
    def _discover_language_voices(self):
        """Discover available voices for different languages"""
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                return
            
            # Common language patterns in voice names
            language_patterns = {
                'en': ['english', 'en_', 'us', 'uk', 'australian', 'david', 'zira', 'hazel'],
                'ur': ['urdu', 'ur_', 'pakistan', 'pakistani'],
                'ps': ['pashto', 'ps_', 'afghan', 'afghanistan'],
                'hi': ['hindi', 'hi_', 'indian', 'india'],
                'ar': ['arabic', 'ar_', 'saudi', 'egypt'],
                'es': ['spanish', 'es_', 'mexico', 'spain'],
                'fr': ['french', 'fr_', 'france'],
                'de': ['german', 'de_', 'germany']
            }
            
            for voice in voices:
                if not hasattr(voice, 'name') or not voice.name:
                    continue
                    
                voice_name_lower = voice.name.lower()
                
                for lang_code, patterns in language_patterns.items():
                    if any(pattern in voice_name_lower for pattern in patterns):
                        if lang_code not in self.language_voices:
                            self.language_voices[lang_code] = []
                        self.language_voices[lang_code].append({
                            'id': voice.id,
                            'name': voice.name,
                            'language': lang_code
                        })
                        break
            
            logging.info(f"Discovered voices for languages: {list(self.language_voices.keys())}")
            
        except Exception as e:
            logging.error(f"Error discovering language voices: {e}")
    
    def set_language(self, language_code: str) -> bool:
        """Set the voice language"""
        language_code = language_code.lower()
        
        # Map common language codes
        lang_map = {
            'urdu': 'ur',
            'pashto': 'ps',
            'pushto': 'ps',
            'english': 'en',
            'hindi': 'hi',
            'arabic': 'ar'
        }
        
        mapped_lang = lang_map.get(language_code, language_code)
        
        if self._set_language_voice(mapped_lang):
            self.current_language = mapped_lang
            logging.info(f"Voice language set to: {mapped_lang}")
            return True
        else:
            logging.warning(f"No voice found for language: {mapped_lang}, using default")
            return False
    
    def _set_language_voice(self, language_code: str) -> bool:
        """Set voice for specific language"""
        try:
            # First try to use discovered language-specific voices
            if language_code in self.language_voices and self.language_voices[language_code]:
                best_voice = self.language_voices[language_code][0]  # Use first available
                self.engine.setProperty('voice', best_voice['id'])
                logging.debug(f"Set voice to: {best_voice['name']} for language: {language_code}")
                return True
            
            # Fallback: try to find voice by manual search
            voices = self.engine.getProperty('voices')
            if not voices:
                return False
            
            # Search patterns for different languages
            search_patterns = {
                'ur': ['urdu', 'pakistan'],
                'ps': ['pashto', 'afghan'],
                'en': ['english', 'david', 'zira', 'hazel', 'microsoft'],
                'hi': ['hindi', 'indian'],
                'ar': ['arabic', 'saudi']
            }
            
            patterns = search_patterns.get(language_code, [language_code])
            
            for voice in voices:
                if not hasattr(voice, 'name') or not voice.name:
                    continue
                    
                voice_name_lower = voice.name.lower()
                if any(pattern in voice_name_lower for pattern in patterns):
                    self.engine.setProperty('voice', voice.id)
                    logging.debug(f"Found and set voice: {voice.name} for language: {language_code}")
                    return True
            
            # If no specific language voice found, use first available voice
            if hasattr(voices[0], 'id'):
                self.engine.setProperty('voice', voices[0].id)
                logging.debug(f"Using default voice for language: {language_code}")
                return True
                
        except Exception as e:
            logging.error(f"Error setting language voice for {language_code}: {e}")
        
        return False
    
    def speak(self, text: str, language: Optional[str] = None) -> bool:
        """Convert text to speech with optional language override"""
        try:
            # Set temporary language if specified
            original_language = None
            if language and language != self.current_language:
                original_language = self.current_language
                self.set_language(language)
            
            def _speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    logging.error(f"Error during speech synthesis: {e}")
            
            # Run speech in separate thread to avoid blocking
            thread = Thread(target=_speak)
            thread.daemon = True
            thread.start()
            
            # Restore original language if it was temporarily changed
            if original_language:
                self.set_language(original_language)
            
            logging.info(f"Speaking in {language or self.current_language}: {text[:50]}...")
            return True
            
        except Exception as e:
            logging.error(f"Error in text-to-speech: {e}")
            return False
    
    def speak_multilingual(self, text_dict: Dict[str, str]) -> bool:
        """Speak text in multiple languages"""
        try:
            current_lang = text_dict.get(self.current_language)
            if current_lang:
                return self.speak(current_lang)
            
            # Fallback to English or first available
            fallback_text = text_dict.get('en', list(text_dict.values())[0])
            fallback_lang = 'en' if 'en' in text_dict else list(text_dict.keys())[0]
            
            return self.speak(fallback_text, fallback_lang)
            
        except Exception as e:
            logging.error(f"Error in multilingual speech: {e}")
            return False
    
    def get_language_info(self) -> Dict:
        """Get current language and available voices information"""
        try:
            voices = self.engine.getProperty('voices')
            current_voice = self.engine.getProperty('voice')
            rate = self.engine.getProperty('rate')
            volume = self.engine.getProperty('volume')
            
            # Get current voice details
            current_voice_info = None
            if voices:
                for voice in voices:
                    if hasattr(voice, 'id') and voice.id == current_voice:
                        current_voice_info = {
                            'id': voice.id,
                            'name': getattr(voice, 'name', 'Unknown'),
                            'language': self.current_language
                        }
                        break
            
            return {
                'current_language': self.current_language,
                'current_voice': current_voice_info,
                'available_languages': list(self.language_voices.keys()),
                'language_voices': self.language_voices,
                'rate': rate,
                'volume': volume,
                'supported_languages': [
                    {'code': 'en', 'name': 'English'},
                    {'code': 'ur', 'name': 'Urdu (اردو)'},
                    {'code': 'ps', 'name': 'Pashto (پښتو)'},
                    {'code': 'hi', 'name': 'Hindi (हिन्दी)'},
                    {'code': 'ar', 'name': 'Arabic (العربية)'}
                ]
            }
        except Exception as e:
            logging.error(f"Error getting language info: {e}")
            return {
                'current_language': self.current_language,
                'error': str(e)
            }
    
    def test_voice(self, language: Optional[str] = None) -> bool:
        """Test voice output with language-specific text"""
        test_texts = {
            'en': 'Voice test successful. I can speak clearly in English.',
            'ur': 'آواز کا ٹیسٹ کامیاب ہے۔ میں اردو میں واضح طور پر بول سکتا ہوں۔',
            'ps': 'د غږ ازموینه بریالۍ وه. زه کولی شم په پښتو کې څرګنده خبرې وکړم.',
            'hi': 'आवाज़ परीक्षण सफल है। मैं हिंदी में स्पष्ट रूप से बोल सकता हूँ।',
            'ar': 'اختبار الصوت ناجح. يمكنني التحدث بوضوح باللغة العربية.'
        }
        
        test_language = language or self.current_language
        test_text = test_texts.get(test_language, test_texts['en'])
        
        return self.speak(test_text, test_language)
    
    def get_available_voices(self) -> List[Dict]:
        """Get list of all available voices"""
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            
            if voices:
                for voice in voices:
                    if hasattr(voice, 'id') and hasattr(voice, 'name'):
                        voice_info = {
                            'id': voice.id,
                            'name': voice.name,
                            'language': 'unknown'
                        }
                        
                        # Try to determine language from voice name
                        voice_name_lower = voice.name.lower()
                        if any(pattern in voice_name_lower for pattern in ['english', 'en_', 'david', 'zira']):
                            voice_info['language'] = 'en'
                        elif any(pattern in voice_name_lower for pattern in ['urdu', 'pakistan']):
                            voice_info['language'] = 'ur'
                        elif any(pattern in voice_name_lower for pattern in ['pashto', 'afghan']):
                            voice_info['language'] = 'ps'
                        elif any(pattern in voice_name_lower for pattern in ['hindi', 'indian']):
                            voice_info['language'] = 'hi'
                        elif any(pattern in voice_name_lower for pattern in ['arabic', 'saudi']):
                            voice_info['language'] = 'ar'
                        
                        voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            logging.error(f"Error getting available voices: {e}")
            return []

# Global enhanced voice service instance
enhanced_voice_service = EnhancedVoiceService()