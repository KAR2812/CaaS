"""
AI service for content generation using OpenAI and Gemini.
"""
import logging
import tiktoken
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy-loaded clients (initialized when first used)
_openai_client = None
_gemini_configured = False


def get_openai_client():
    """Lazy-load OpenAI client."""
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def get_gemini_model():
    """Lazy-load Gemini configuration."""
    global _gemini_configured
    if not _gemini_configured:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True
    import google.generativeai as genai
    return genai.GenerativeModel(settings.GEMINI_MODEL)


class AIContentGenerator:
    """
    Service class for AI content generation with multiple providers.
    """
    
    PLATFORM_CHAR_LIMITS = {
        'twitter': 280,
        'linkedin': 1300,
        'instagram': 2200,
    }
    
    @staticmethod
    def build_prompt(platform, tone, audience, user_prompt):
        """Build the system + user prompt for AI."""
        char_limit = AIContentGenerator.PLATFORM_CHAR_LIMITS.get(platform, 280)
        
        system_prompt = f"""You are an expert social media copywriter. Generate engaging content for {platform}.

Platform: {platform}
Tone: {tone}
Audience: {audience or 'general'}
Character Limit: {char_limit}

Requirements:
- Stay within character limit
- Include relevant hashtags (2-3 for Twitter, 3-5 for others)
- Optimize for engagement
- Respect platform norms and culture
- Use emojis appropriately

Output only the final post text, ready to publish."""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def count_tokens(text, model='gpt-4'):
        """Count tokens using tiktoken."""
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token counting failed: {e}, using estimate")
            return len(text) // 4  # Rough estimate
    
    @staticmethod
    def generate_with_openai(platform, tone, audience, user_prompt):
        """Generate content using OpenAI GPT."""
        system_prompt, user_message = AIContentGenerator.build_prompt(
            platform, tone, audience, user_prompt
        )
        
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            generated_text = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            
            return {
                'success': True,
                'text': generated_text,
                'tokens': tokens_used,
                'provider': 'openai'
            }
        
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'openai'
            }
    
    @staticmethod
    def generate_with_gemini(platform, tone, audience, user_prompt):
        """Generate content using Google Gemini."""
        system_prompt, user_message = AIContentGenerator.build_prompt(
            platform, tone, audience, user_prompt
        )
        
        try:
            model = get_gemini_model()
            full_prompt = f"{system_prompt}\n\nUser Request: {user_message}"
            
            response = model.generate_content(full_prompt)
            generated_text = response.text.strip()
            
            # Estimate tokens (Gemini API doesn't provide exact count in same way)
            tokens_used = AIContentGenerator.count_tokens(system_prompt + user_message + generated_text)
            
            return {
                'success': True,
                'text': generated_text,
                'tokens': tokens_used,
                'provider': 'gemini'
            }
        
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'gemini'
            }
    
    @staticmethod
    def generate(platform, tone, audience, user_prompt, provider='openai'):
        """
        Main generation method with fallback.
        
        Args:
            platform: twitter, linkedin, instagram
            tone: professional, casual, etc.
            audience: target audience description
            user_prompt: user's content request
            provider: 'openai' or 'gemini'
        
        Returns:
            dict with success, text, tokens, provider
        """
        # Try primary provider
        if provider == 'openai':
            result = AIContentGenerator.generate_with_openai(platform, tone, audience, user_prompt)
            # Fallback to Gemini if OpenAI fails
            if not result['success']:
                logger.info("Falling back to Gemini after OpenAI failure")
                result = AIContentGenerator.generate_with_gemini(platform, tone, audience, user_prompt)
        else:
            result = AIContentGenerator.generate_with_gemini(platform, tone, audience, user_prompt)
            # Fallback to OpenAI if Gemini fails
            if not result['success']:
                logger.info("Falling back to OpenAI after Gemini failure")
                result = AIContentGenerator.generate_with_openai(platform, tone, audience, user_prompt)
        
        return result
