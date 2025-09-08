import json
import logging
import os
import requests
import google.generativeai as genai
from google.genai import types
from pydantic import BaseModel
import base64

# This API key is from Gemini Developer API Key, not vertex AI API Key
try:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and gemini_key != "default_gemini_key":
        client = genai.Client(api_key=gemini_key)
    else:
        client = None
except:
    client = None

class GeminiService:
    def __init__(self):
        self.client = client
    
    def generate_text_response(self, prompt):
        """Generate text response using multiple AI services with fallback"""
        
        # Try Gemini API first
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text
            except Exception as e:
                logging.warning(f"Gemini API failed: {e}")
        
        # Try Hugging Face API
        hf_response = self._try_huggingface_text(prompt)
        if hf_response:
            return hf_response
        
        # Try AIML API
        aiml_response = self._try_aiml_text(prompt)
        if aiml_response:
            return aiml_response
        
        # Fallback response
        return "I'm currently unable to generate a response. Please check your AI API keys in settings or try again later."
    
    def _try_huggingface_text(self, prompt):
        """Try Hugging Face API for text generation"""
        try:
            hf_key = os.getenv('HUGGINGFACE_API_KEY')
            if not hf_key:
                return None
                
            headers = {"Authorization": f"Bearer {hf_key}"}
            
            # Try multiple models
            models = [
                "microsoft/DialoGPT-medium",
                "facebook/blenderbot-400M-distill",
                "google/flan-t5-base"
            ]
            
            for model in models:
                try:
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json={"inputs": prompt},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            if generated_text and len(generated_text.strip()) > 0:
                                return generated_text
                except:
                    continue
                    
        except Exception as e:
            logging.warning(f"Hugging Face API failed: {e}")
        
        return None
    
    def _try_aiml_text(self, prompt):
        """Try AIML API for text generation"""
        try:
            aiml_key = os.getenv('AIML_API_KEY')
            if not aiml_key:
                return None
                
            headers = {
                "Authorization": f"Bearer {aiml_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",  # AIML API supports multiple models
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.aimlapi.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                    
        except Exception as e:
            logging.warning(f"AIML API failed: {e}")
        
        return None
    
    def generate_facebook_post(self, topic, include_hashtags=True):
        """Generate Facebook post content using multiple AI services"""
        prompt = f"""Create an engaging Facebook post about: {topic}
        
        Requirements:
        - Keep it under 280 characters
        - Make it engaging and social media friendly
        - Include relevant emojis
        {'- Add 3-5 relevant hashtags at the end' if include_hashtags else '- No hashtags needed'}
        - Make it sound natural and personal
        """
        
        # Use the same fallback system as text generation
        response = self.generate_text_response(prompt)
        
        if response and not response.startswith("I'm currently unable"):
            return response
        
        # Fallback post content
        fallback_posts = [
            f"🌟 Excited to share something about {topic}! What are your thoughts? Share in the comments below! 💬✨ #thoughts #share #community",
            f"💡 {topic} is such an interesting topic! I'd love to hear your perspectives. Drop a comment! 👇 #discussion #ideas #community",
            f"🚀 Just thinking about {topic}... Amazing how much there is to explore! What fascinates you most? 🤔💭 #explore #learn #curious"
        ]
        
        import random
        return random.choice(fallback_posts)
    
    def generate_image(self, prompt, image_path):
        """Generate image using multiple AI services with fallback"""
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Try Gemini API first
        if self.client:
            success, result = self._try_gemini_image(prompt, image_path)
            if success:
                return success, result
        
        # Try DeepAI API
        success, result = self._try_deepai_image(prompt, image_path)
        if success:
            return success, result
        
        # Try Hugging Face API
        success, result = self._try_huggingface_image(prompt, image_path)
        if success:
            return success, result
        
        # Try Replicate API
        success, result = self._try_replicate_image(prompt, image_path)
        if success:
            return success, result
        
        return False, "All image generation services failed. Please check your API keys in settings."
    
    def _try_gemini_image(self, prompt, image_path):
        """Try Gemini API for image generation"""
        try:
            # Enhance the prompt for better image generation
            enhanced_prompt = f"""Create a high-quality, visually appealing image: {prompt}
            
            Style requirements:
            - Professional and polished look
            - Good composition and lighting
            - Vibrant but not oversaturated colors
            - Clear and detailed
            """
            
            response = self.client.models.generate_content(
                # IMPORTANT: only this gemini model supports image generation
                model="gemini-2.0-flash-preview-image-generation",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )

            if not response.candidates:
                return False, "No image generated"

            try:
                content = response.candidates[0].content
                if not content or not content.parts:
                    return False, "No content in response"

                for part in content.parts:
                    if part.inline_data and part.inline_data.data:
                        with open(image_path, 'wb') as f:
                            f.write(part.inline_data.data)
                        logging.info(f"Image saved via Gemini API: {image_path}")
                        return True, f"Image generated successfully via Gemini API"
                
                return False, "No image data found in response"
                
            except Exception as e:
                return False, f"Error saving Gemini image: {str(e)}"
                
        except Exception as e:
            logging.warning(f"Gemini image generation failed: {e}")
            return False, f"Gemini API error: {str(e)}"
    
    def _try_deepai_image(self, prompt, image_path):
        """Try DeepAI for image generation (FREE)"""
        try:
            deepai_key = os.getenv('DEEPAI_API_KEY')
            if not deepai_key:
                return False, "DeepAI API key not found"
            
            response = requests.post(
                "https://api.deepai.org/api/text2img",
                data={
                    'text': prompt,
                },
                headers={'api-key': deepai_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get('output_url')
                
                if image_url:
                    # Download the image
                    img_response = requests.get(image_url, timeout=30)
                    if img_response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(img_response.content)
                        logging.info(f"Image saved via DeepAI: {image_path}")
                        return True, f"Image generated successfully via DeepAI (FREE)"
            
            return False, "DeepAI API request failed"
            
        except Exception as e:
            logging.warning(f"DeepAI image generation failed: {e}")
            return False, f"DeepAI error: {str(e)}"
    
    def _try_huggingface_image(self, prompt, image_path):
        """Try Hugging Face for image generation (FREE)"""
        try:
            hf_key = os.getenv('HUGGINGFACE_API_KEY')
            if not hf_key:
                return False, "Hugging Face API key not found"
            
            headers = {"Authorization": f"Bearer {hf_key}"}
            
            # Try multiple Stable Diffusion models
            models = [
                "stabilityai/stable-diffusion-2-1",
                "runwayml/stable-diffusion-v1-5",
                "CompVis/stable-diffusion-v1-4"
            ]
            
            for model in models:
                try:
                    response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        headers=headers,
                        json={"inputs": prompt},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        logging.info(f"Image saved via Hugging Face: {image_path}")
                        return True, f"Image generated successfully via Hugging Face (FREE)"
                except:
                    continue
            
            return False, "All Hugging Face models failed"
            
        except Exception as e:
            logging.warning(f"Hugging Face image generation failed: {e}")
            return False, f"Hugging Face error: {str(e)}"
    
    def _try_replicate_image(self, prompt, image_path):
        """Try Replicate for image generation (FREE TIER)"""
        try:
            replicate_key = os.getenv('REPLICATE_API_KEY')
            if not replicate_key:
                return False, "Replicate API key not found"
            
            headers = {
                "Authorization": f"Token {replicate_key}",
                "Content-Type": "application/json"
            }
            
            # Use FLUX model which is very good
            data = {
                "version": "schnell",  # Fast version
                "input": {
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "1:1",
                    "output_format": "png",
                    "output_quality": 80
                }
            }
            
            response = requests.post(
                "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                # Replicate usually returns URLs, would need to poll for completion
                # For now, return success with the prediction ID
                return False, "Replicate API requires polling - not implemented yet"
            
            return False, "Replicate API request failed"
            
        except Exception as e:
            logging.warning(f"Replicate image generation failed: {e}")
            return False, f"Replicate error: {str(e)}"
    
    def generate_auto_reply(self, original_message, context="general"):
        """Generate intelligent auto-reply for messages using multiple AI services"""
        prompt = f"""Generate a helpful and professional auto-reply for this message:
        
        Original message: "{original_message}"
        Context: {context}
        
        Requirements:
        - Keep it brief and friendly
        - Acknowledge their message
        - Be helpful and professional
        - Don't make promises you can't keep
        - Sound natural and human-like
        """
        
        # Use the same fallback system as text generation
        response = self.generate_text_response(prompt)
        
        if response and not response.startswith("I'm currently unable"):
            return response
        
        # Fallback auto-reply messages
        fallback_replies = [
            "Thank you for your message! I've received it and will get back to you as soon as possible. Have a great day! 😊",
            "Hi there! Thanks for reaching out. I'll review your message and respond shortly. Appreciate your patience! 🙏",
            "Hello! I've received your message and will get back to you soon. Thanks for contacting me! 💌"
        ]
        
        import random
        return random.choice(fallback_replies)

# Global Gemini service instance
gemini_service = GeminiService()
