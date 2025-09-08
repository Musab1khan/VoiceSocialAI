"""
Multi-AI Provider Service for comprehensive AI capabilities
Supports multiple free AI services like OpenRouter, DeepSeek, Hugging Face, etc.
"""

import os
import logging
import requests
import json
import base64
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class AIProvider:
    name: str
    base_url: str
    api_key: str
    models: Dict[str, str]
    capabilities: List[str]

class MultiAIService:
    def __init__(self):
        self.providers = self._initialize_providers()
        self.current_provider = 'openrouter'  # Default
        self.current_language = 'en'  # Default language
        
    def _initialize_providers(self) -> Dict[str, AIProvider]:
        """Initialize all available AI providers"""
        providers = {}
        
        # OpenRouter (Free models available)
        providers['openrouter'] = AIProvider(
            name="OpenRouter",
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            models={
                'text': 'deepseek/deepseek-r1-distill-llama-70b:free',
                'fast_text': 'microsoft/phi-3-mini-128k-instruct:free',
                'image': 'stability-ai/stable-diffusion-3-medium:free',
                'code': 'deepseek/deepseek-coder:free'
            },
            capabilities=['text', 'code', 'reasoning', 'image']
        )
        
        # DeepSeek (Direct API)
        providers['deepseek'] = AIProvider(
            name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            models={
                'text': 'deepseek-chat',
                'reasoning': 'deepseek-reasoner',
                'code': 'deepseek-coder'
            },
            capabilities=['text', 'code', 'reasoning', 'math']
        )
        
        # Hugging Face (Free Inference API)
        providers['huggingface'] = AIProvider(
            name="Hugging Face",
            base_url="https://api-inference.huggingface.co",
            api_key=os.environ.get("HUGGINGFACE_API_KEY", ""),
            models={
                'text': 'microsoft/DialoGPT-large',
                'image': 'runwayml/stable-diffusion-v1-5',
                'image_xl': 'stabilityai/stable-diffusion-xl-base-1.0',
                'flux': 'black-forest-labs/FLUX.1-dev',
                'translation': 'facebook/mbart-large-50-many-to-many-mmt'
            },
            capabilities=['text', 'image', 'translation', 'audio']
        )
        
        # Gemini (Fallback)
        providers['gemini'] = AIProvider(
            name="Google Gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key=os.environ.get("GEMINI_API_KEY", ""),
            models={
                'text': 'gemini-2.5-flash',
                'image': 'gemini-2.0-flash-preview-image-generation',
                'vision': 'gemini-2.5-pro'
            },
            capabilities=['text', 'image', 'vision', 'multimodal']
        )
        
        # Together AI (Free credits)
        providers['together'] = AIProvider(
            name="Together AI",
            base_url="https://api.together.xyz/v1",
            api_key=os.environ.get("TOGETHER_API_KEY", ""),
            models={
                'text': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'image': 'stabilityai/stable-diffusion-xl-base-1.0',
                'code': 'codellama/CodeLlama-34b-Instruct-hf'
            },
            capabilities=['text', 'code', 'image']
        )
        
        return providers
    
    def set_language(self, language_code: str):
        """Set the primary language for responses"""
        language_map = {
            'ur': 'urdu',
            'ps': 'pashto', 
            'pa': 'pashto',
            'en': 'english',
            'hi': 'hindi',
            'ar': 'arabic'
        }
        
        self.current_language = language_map.get(language_code.lower(), language_code)
        logging.info(f"Language set to: {self.current_language}")
    
    def get_language_prompt(self, base_prompt: str) -> str:
        """Add language instruction to prompt"""
        if self.current_language == 'urdu':
            return f"{base_prompt}\n\nPlease respond in Urdu (اردو). Use clear and simple Urdu language."
        elif self.current_language == 'pashto':
            return f"{base_prompt}\n\nPlease respond in Pashto (پښتو). Use clear and simple Pashto language."
        elif self.current_language == 'english':
            return base_prompt
        else:
            return f"{base_prompt}\n\nPlease respond in {self.current_language} language."
    
    def generate_text(self, prompt: str, provider: str = None, model_type: str = 'text') -> Tuple[bool, str]:
        """Generate text using specified or best available provider"""
        providers_to_try = [provider] if provider else ['openrouter', 'deepseek', 'gemini', 'huggingface']
        
        # Add language context to prompt
        enhanced_prompt = self.get_language_prompt(prompt)
        
        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue
                
            provider = self.providers[provider_name]
            if not provider.api_key or 'text' not in provider.capabilities:
                continue
            
            try:
                success, result = self._call_text_api(provider, enhanced_prompt, model_type)
                if success:
                    return True, result
            except Exception as e:
                logging.error(f"Error with {provider_name}: {e}")
                continue
        
        return False, "All AI providers failed to generate text response."
    
    def _call_text_api(self, provider: AIProvider, prompt: str, model_type: str) -> Tuple[bool, str]:
        """Call text generation API for specific provider"""
        
        if provider.name == "OpenRouter":
            return self._call_openrouter_text(provider, prompt, model_type)
        elif provider.name == "DeepSeek":
            return self._call_deepseek_text(provider, prompt, model_type)
        elif provider.name == "Hugging Face":
            return self._call_huggingface_text(provider, prompt)
        elif provider.name == "Google Gemini":
            return self._call_gemini_text(provider, prompt)
        elif provider.name == "Together AI":
            return self._call_together_text(provider, prompt, model_type)
        
        return False, f"Provider {provider.name} not implemented"
    
    def _call_openrouter_text(self, provider: AIProvider, prompt: str, model_type: str) -> Tuple[bool, str]:
        """Call OpenRouter API"""
        model = provider.models.get(model_type, provider.models['text'])
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://ai-voice-assistant.replit.app',
            'X-Title': 'AI Voice Assistant'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1000
        }
        
        response = requests.post(f"{provider.base_url}/chat/completions", 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result['choices'][0]['message']['content']
        else:
            return False, f"OpenRouter API error: {response.text}"
    
    def _call_deepseek_text(self, provider: AIProvider, prompt: str, model_type: str) -> Tuple[bool, str]:
        """Call DeepSeek API"""
        model = provider.models.get(model_type, provider.models['text'])
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful AI assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            'stream': False
        }
        
        response = requests.post(f"{provider.base_url}/chat/completions",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result['choices'][0]['message']['content']
        else:
            return False, f"DeepSeek API error: {response.text}"
    
    def _call_huggingface_text(self, provider: AIProvider, prompt: str) -> Tuple[bool, str]:
        """Call Hugging Face Inference API"""
        model = provider.models['text']
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {'inputs': prompt}
        
        response = requests.post(f"{provider.base_url}/models/{model}",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return True, result[0].get('generated_text', prompt)
            return True, str(result)
        else:
            return False, f"Hugging Face API error: {response.text}"
    
    def _call_gemini_text(self, provider: AIProvider, prompt: str) -> Tuple[bool, str]:
        """Call Gemini API"""
        # Use existing gemini service
        from services.gemini_service import gemini_service
        try:
            result = gemini_service.generate_text_response(prompt)
            return True, result
        except Exception as e:
            return False, f"Gemini API error: {str(e)}"
    
    def _call_together_text(self, provider: AIProvider, prompt: str, model_type: str) -> Tuple[bool, str]:
        """Call Together AI API"""
        model = provider.models.get(model_type, provider.models['text'])
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 1000
        }
        
        response = requests.post(f"{provider.base_url}/chat/completions",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result['choices'][0]['message']['content']
        else:
            return False, f"Together AI error: {response.text}"
    
    def generate_image(self, prompt: str, image_path: str, provider: str = None) -> Tuple[bool, str]:
        """Generate image using best available provider"""
        providers_to_try = [provider] if provider else ['huggingface', 'openrouter', 'together', 'gemini']
        
        # Enhance prompt for better results
        enhanced_prompt = f"High quality, detailed, professional: {prompt}"
        
        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue
                
            provider = self.providers[provider_name]
            if not provider.api_key or 'image' not in provider.capabilities:
                continue
            
            try:
                success, result = self._call_image_api(provider, enhanced_prompt, image_path)
                if success:
                    return True, result
            except Exception as e:
                logging.error(f"Image generation error with {provider_name}: {e}")
                continue
        
        return False, "All image generation providers failed."
    
    def _call_image_api(self, provider: AIProvider, prompt: str, image_path: str) -> Tuple[bool, str]:
        """Call image generation API for specific provider"""
        
        if provider.name == "Hugging Face":
            return self._call_huggingface_image(provider, prompt, image_path)
        elif provider.name == "OpenRouter":
            return self._call_openrouter_image(provider, prompt, image_path)
        elif provider.name == "Google Gemini":
            return self._call_gemini_image(provider, prompt, image_path)
        elif provider.name == "Together AI":
            return self._call_together_image(provider, prompt, image_path)
        
        return False, f"Image generation not implemented for {provider.name}"
    
    def _call_huggingface_image(self, provider: AIProvider, prompt: str, image_path: str) -> Tuple[bool, str]:
        """Call Hugging Face image generation"""
        # Try multiple models for best results
        models_to_try = ['image_xl', 'flux', 'image']
        
        for model_key in models_to_try:
            if model_key not in provider.models:
                continue
                
            model = provider.models[model_key]
            
            headers = {
                'Authorization': f'Bearer {provider.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {'inputs': prompt}
            
            try:
                response = requests.post(f"{provider.base_url}/models/{model}",
                                       headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    return True, f"Image generated successfully using {model}"
            except Exception as e:
                logging.error(f"HF model {model} failed: {e}")
                continue
        
        return False, "All Hugging Face models failed"
    
    def _call_openrouter_image(self, provider: AIProvider, prompt: str, image_path: str) -> Tuple[bool, str]:
        """Call OpenRouter image generation"""
        model = provider.models.get('image', 'stability-ai/stable-diffusion-3-medium:free')
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'prompt': prompt,
            'n': 1,
            'size': '1024x1024'
        }
        
        response = requests.post(f"{provider.base_url}/images/generations",
                               headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Download the image
            img_response = requests.get(image_url)
            with open(image_path, 'wb') as f:
                f.write(img_response.content)
            
            return True, "Image generated successfully via OpenRouter"
        else:
            return False, f"OpenRouter image error: {response.text}"
    
    def _call_gemini_image(self, provider: AIProvider, prompt: str, image_path: str) -> Tuple[bool, str]:
        """Call Gemini image generation"""
        from services.gemini_service import gemini_service
        try:
            success, result = gemini_service.generate_image(prompt, image_path)
            return success, result
        except Exception as e:
            return False, f"Gemini image error: {str(e)}"
    
    def _call_together_image(self, provider: AIProvider, prompt: str, image_path: str) -> Tuple[bool, str]:
        """Call Together AI image generation"""
        model = provider.models.get('image', 'stabilityai/stable-diffusion-xl-base-1.0')
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'prompt': prompt,
            'steps': 20,
            'n': 1
        }
        
        response = requests.post(f"{provider.base_url}/images/generations",
                               headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            image_b64 = result['data'][0]['b64_json']
            
            # Decode and save image
            image_data = base64.b64decode(image_b64)
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return True, "Image generated successfully via Together AI"
        else:
            return False, f"Together AI image error: {response.text}"
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using free search APIs"""
        search_providers = [
            self._search_duckduckgo,
            self._search_serper,
            self._search_searchapi
        ]
        
        for search_func in search_providers:
            try:
                results = search_func(query, num_results)
                if results:
                    return results
            except Exception as e:
                logging.error(f"Search provider failed: {e}")
                continue
        
        return []
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API (Free)"""
        try:
            import requests
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                results = []
                
                # Add abstract if available
                if data.get('Abstract'):
                    results.append({
                        'title': data.get('AbstractText', 'DuckDuckGo Result'),
                        'url': data.get('AbstractURL', ''),
                        'snippet': data.get('Abstract', '')
                    })
                
                # Add related topics
                for topic in data.get('RelatedTopics', [])[:num_results-1]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append({
                            'title': topic.get('Text', '')[:50] + '...',
                            'url': topic.get('FirstURL', ''),
                            'snippet': topic.get('Text', '')
                        })
                
                return results[:num_results]
        except Exception as e:
            logging.error(f"DuckDuckGo search error: {e}")
        
        return []
    
    def _search_serper(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Serper API (has free tier)"""
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            return []
        
        try:
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'q': query,
                'num': num_results
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                results_data = response.json()
                
                results = []
                for item in results_data.get('organic', [])[:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
                
                return results
        except Exception as e:
            logging.error(f"Serper search error: {e}")
        
        return []
    
    def _search_searchapi(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using SearchAPI (has free tier)"""
        api_key = os.environ.get("SEARCHAPI_API_KEY")
        if not api_key:
            return []
        
        try:
            url = "https://www.searchapi.io/api/v1/search"
            params = {
                'api_key': api_key,
                'q': query,
                'num': num_results,
                'engine': 'google'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results_data = response.json()
                
                results = []
                for item in results_data.get('organic_results', [])[:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
                
                return results
        except Exception as e:
            logging.error(f"SearchAPI error: {e}")
        
        return []
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> Tuple[bool, str]:
        """Translate text using free translation APIs"""
        
        # Try Hugging Face translation first
        if 'huggingface' in self.providers and self.providers['huggingface'].api_key:
            try:
                success, result = self._translate_huggingface(text, target_language, source_language)
                if success:
                    return True, result
            except Exception as e:
                logging.error(f"HF translation error: {e}")
        
        # Fallback to AI-based translation
        if target_language.lower() in ['urdu', 'ur']:
            prompt = f"Translate the following text to Urdu (اردو): {text}"
        elif target_language.lower() in ['pashto', 'ps', 'pa']:
            prompt = f"Translate the following text to Pashto (پښتو): {text}"
        else:
            prompt = f"Translate the following text to {target_language}: {text}"
        
        success, result = self.generate_text(prompt, model_type='text')
        return success, result
    
    def _translate_huggingface(self, text: str, target_lang: str, source_lang: str) -> Tuple[bool, str]:
        """Translate using Hugging Face MBART model"""
        provider = self.providers['huggingface']
        model = provider.models['translation']
        
        # Map language codes
        lang_map = {
            'urdu': 'ur_PK',
            'ur': 'ur_PK', 
            'pashto': 'ps_AF',
            'ps': 'ps_AF',
            'english': 'en_XX',
            'en': 'en_XX'
        }
        
        target_code = lang_map.get(target_lang.lower(), target_lang)
        
        headers = {
            'Authorization': f'Bearer {provider.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'inputs': text,
            'parameters': {
                'src_lang': source_lang,
                'tgt_lang': target_code
            }
        }
        
        response = requests.post(f"{provider.base_url}/models/{model}",
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return True, result[0].get('translation_text', text)
            return True, str(result)
        else:
            return False, f"Translation error: {response.text}"
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all available providers"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                'name': provider.name,
                'has_api_key': bool(provider.api_key and provider.api_key != ""),
                'capabilities': provider.capabilities,
                'models': provider.models
            }
        
        return status
    
    def set_primary_provider(self, provider_name: str):
        """Set the primary AI provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            logging.info(f"Primary AI provider set to: {provider_name}")
            return True
        return False

# Global multi-AI service instance
multi_ai_service = MultiAIService()