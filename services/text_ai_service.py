import os
import logging
import json
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime

class TextAIService:
    """
    Advanced Text AI Service for natural content generation
    Supports multiple AI providers and content types
    """
    
    def __init__(self):
        self.providers = {
            'gemini': self._use_gemini,
            'openai': self._use_openai,
            'huggingface': self._use_huggingface,
            'aiml': self._use_aiml
        }
        
        # Content type templates
        self.content_templates = {
            'social_post': {
                'system': "You are a social media expert. Create engaging, natural posts with relevant hashtags. Write in a conversational, human-like tone.",
                'max_length': 280,
                'include_hashtags': True
            },
            'blog_article': {
                'system': "You are a professional blog writer. Create well-structured, informative articles with proper headings, engaging content, and SEO optimization.",
                'max_length': 2000,
                'include_hashtags': True
            },
            'email_reply': {
                'system': "You are a helpful assistant writing professional yet friendly email replies. Be concise, helpful, and maintain a warm tone.",
                'max_length': 500,
                'include_hashtags': False
            },
            'product_description': {
                'system': "You are a marketing copywriter. Create compelling product descriptions that highlight benefits and features naturally.",
                'max_length': 300,
                'include_hashtags': True
            },
            'news_article': {
                'system': "You are a journalist writing news articles. Provide factual, well-structured content with proper headlines and clear information.",
                'max_length': 1500,
                'include_hashtags': False
            },
            'creative_story': {
                'system': "You are a creative writer. Write engaging, imaginative stories with vivid descriptions and compelling narratives.",
                'max_length': 1000,
                'include_hashtags': False
            },
            'tutorial': {
                'system': "You are an educational content creator. Write clear, step-by-step tutorials that are easy to follow and understand.",
                'max_length': 1200,
                'include_hashtags': True
            },
            'review': {
                'system': "You are writing honest, detailed reviews. Provide balanced perspectives covering pros, cons, and personal insights.",
                'max_length': 600,
                'include_hashtags': True
            }
        }
        
        # Hashtag categories
        self.hashtag_categories = {
            'technology': ['#tech', '#innovation', '#ai', '#digital', '#future', '#gadgets', '#software'],
            'business': ['#business', '#entrepreneur', '#startup', '#marketing', '#success', '#growth'],
            'lifestyle': ['#lifestyle', '#wellness', '#health', '#fitness', '#motivation', '#inspiration'],
            'education': ['#education', '#learning', '#knowledge', '#skills', '#tutorial', '#howto'],
            'entertainment': ['#entertainment', '#fun', '#trending', '#viral', '#creative', '#art'],
            'travel': ['#travel', '#adventure', '#explore', '#wanderlust', '#vacation', '#journey'],
            'food': ['#food', '#cooking', '#recipe', '#delicious', '#foodie', '#culinary'],
            'fashion': ['#fashion', '#style', '#outfit', '#trend', '#beauty', '#design']
        }
    
    def generate_content(self, 
                        content_type: str, 
                        topic: str, 
                        tone: str = 'friendly', 
                        language: str = 'english',
                        custom_instructions: str = '') -> Dict:
        """
        Generate content using the best available AI provider
        
        Args:
            content_type: Type of content (social_post, blog_article, etc.)
            topic: The main topic/subject
            tone: Writing tone (friendly, professional, casual, formal)
            language: Target language
            custom_instructions: Additional specific instructions
            
        Returns:
            Dict containing success status, content, and metadata
        """
        try:
            # Validate content type
            if content_type not in self.content_templates:
                return {
                    'success': False,
                    'error': f'Unsupported content type: {content_type}',
                    'available_types': list(self.content_templates.keys())
                }
            
            # Get template configuration
            template = self.content_templates[content_type]
            
            # Build comprehensive prompt
            prompt = self._build_prompt(
                content_type=content_type,
                topic=topic,
                tone=tone,
                language=language,
                template=template,
                custom_instructions=custom_instructions
            )
            
            # Try providers in order of preference
            provider_order = ['gemini', 'openai', 'huggingface', 'aiml']
            
            for provider in provider_order:
                if self._is_provider_available(provider):
                    try:
                        content = self.providers[provider](prompt, template['max_length'])
                        if content:
                            # Post-process content
                            processed_content = self._post_process_content(
                                content=content,
                                content_type=content_type,
                                include_hashtags=template['include_hashtags'],
                                topic=topic
                            )
                            
                            return {
                                'success': True,
                                'content': processed_content['text'],
                                'hashtags': processed_content['hashtags'],
                                'word_count': len(processed_content['text'].split()),
                                'provider': provider,
                                'content_type': content_type,
                                'generated_at': datetime.utcnow().isoformat()
                            }
                    except Exception as e:
                        logging.warning(f"Provider {provider} failed: {e}")
                        continue
            
            return {
                'success': False,
                'error': 'All AI providers failed or are unavailable'
            }
            
        except Exception as e:
            logging.error(f"Error in text generation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(self, content_type: str, topic: str, tone: str, 
                     language: str, template: Dict, custom_instructions: str) -> str:
        """Build comprehensive prompt for AI generation"""
        
        # Base system instruction
        system_prompt = template['system']
        
        # Add tone specification
        tone_instructions = {
            'friendly': "Use a warm, approachable tone that feels like talking to a friend.",
            'professional': "Maintain a polished, business-appropriate tone.",
            'casual': "Write in a relaxed, conversational style.",
            'formal': "Use proper, structured language appropriate for official contexts.",
            'enthusiastic': "Write with energy and excitement about the topic.",
            'informative': "Focus on providing clear, educational information."
        }
        
        # Add language specification
        language_instruction = f"Write entirely in {language}."
        if language.lower() != 'english':
            language_instruction += " Ensure natural, native-like expression in this language."
        
        # Build complete prompt
        prompt = f"""
{system_prompt}

CONTENT TYPE: {content_type.replace('_', ' ').title()}
TOPIC: {topic}
TONE: {tone_instructions.get(tone, tone)}
LANGUAGE: {language_instruction}
MAX LENGTH: Approximately {template['max_length']} characters

{custom_instructions if custom_instructions else ''}

REQUIREMENTS:
1. Write naturally like a human, not like AI
2. Make it engaging and valuable to readers
3. Include relevant details and context
4. Ensure proper grammar and flow
5. Make it feel authentic and personal
"""
        
        if template['include_hashtags']:
            prompt += "\n6. Include 3-5 relevant hashtags naturally integrated or at the end"
        
        prompt += f"\n\nNow write compelling {content_type.replace('_', ' ')} content about: {topic}"
        
        return prompt
    
    def _post_process_content(self, content: str, content_type: str, 
                            include_hashtags: bool, topic: str) -> Dict:
        """Post-process generated content"""
        
        # Extract hashtags if they exist
        hashtags = []
        if include_hashtags:
            # Find hashtags in content
            import re
            hashtag_matches = re.findall(r'#\w+', content)
            hashtags.extend(hashtag_matches)
            
            # Add relevant hashtags if none found
            if not hashtags:
                hashtags = self._generate_hashtags(topic, content_type)
        
        # Clean up content
        processed_text = content.strip()
        
        # Remove duplicate hashtags from text if we're adding them separately
        if hashtags and include_hashtags:
            for hashtag in set(hashtags):
                processed_text = processed_text.replace(hashtag, '').strip()
        
        return {
            'text': processed_text,
            'hashtags': list(set(hashtags))  # Remove duplicates
        }
    
    def _generate_hashtags(self, topic: str, content_type: str) -> List[str]:
        """Generate relevant hashtags based on topic and content type"""
        hashtags = []
        topic_lower = topic.lower()
        
        # Check each category for relevance
        for category, tags in self.hashtag_categories.items():
            if any(keyword in topic_lower for keyword in [category]):
                hashtags.extend(tags[:3])  # Take first 3 from relevant category
                break
        
        # Add content-type specific hashtags
        if content_type == 'blog_article':
            hashtags.extend(['#blog', '#article', '#content'])
        elif content_type == 'tutorial':
            hashtags.extend(['#tutorial', '#guide', '#howto'])
        elif content_type == 'review':
            hashtags.extend(['#review', '#honest', '#opinion'])
        
        # Add topic as hashtag if suitable
        topic_hashtag = '#' + topic.replace(' ', '').lower()[:15]
        if len(topic_hashtag) > 2:
            hashtags.append(topic_hashtag)
        
        return hashtags[:5]  # Limit to 5 hashtags
    
    def _is_provider_available(self, provider: str) -> bool:
        """Check if AI provider is available with valid API key"""
        if provider == 'gemini':
            return bool(os.getenv('GEMINI_API_KEY'))
        elif provider == 'openai':
            return bool(os.getenv('OPENAI_API_KEY'))
        elif provider == 'huggingface':
            return bool(os.getenv('HUGGINGFACE_API_KEY'))
        elif provider == 'aiml':
            return bool(os.getenv('AIML_API_KEY'))
        return False
    
    def _use_gemini(self, prompt: str, max_length: int) -> Optional[str]:
        """Use Google Gemini API for text generation"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return None
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_length // 2,  # Rough token estimate
                    temperature=0.7,
                    top_p=0.8
                )
            )
            
            return response.text if response.text else None
            
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return None
    
    def _use_openai(self, prompt: str, max_length: int) -> Optional[str]:
        """Use OpenAI API for text generation"""
        try:
            from openai import OpenAI
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return None
                
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length // 3,  # Conservative token estimate
                temperature=0.7,
                top_p=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return None
    
    def _use_huggingface(self, prompt: str, max_length: int) -> Optional[str]:
        """Use Hugging Face API for text generation"""
        try:
            api_key = os.getenv('HUGGINGFACE_API_KEY')
            if not api_key:
                return None
                
            headers = {"Authorization": f"Bearer {api_key}"}
            
            # Use a good text generation model
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and 'generated_text' in result[0]:
                    return result[0]['generated_text'].strip()
                    
            return None
            
        except Exception as e:
            logging.error(f"Hugging Face API error: {e}")
            return None
    
    def _use_aiml(self, prompt: str, max_length: int) -> Optional[str]:
        """Use AI/ML API for text generation"""
        try:
            api_key = os.getenv('AIML_API_KEY')
            if not api_key:
                return None
                
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",  # or another available model
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_length // 3,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.aimlapi.com/chat/completions", 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                    
            return None
            
        except Exception as e:
            logging.error(f"AI/ML API error: {e}")
            return None
    
    def get_available_content_types(self) -> List[Dict]:
        """Get list of available content types with descriptions"""
        return [
            {
                'type': key,
                'name': key.replace('_', ' ').title(),
                'description': template['system'].split('.')[0],
                'max_length': template['max_length'],
                'includes_hashtags': template['include_hashtags']
            }
            for key, template in self.content_templates.items()
        ]
    
    def get_provider_status(self) -> Dict:
        """Get status of all AI providers"""
        return {
            provider: self._is_provider_available(provider)
            for provider in self.providers.keys()
        }

# Create global instance
text_ai_service = TextAIService()