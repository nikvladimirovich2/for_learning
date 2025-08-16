import requests
import json
import time
from typing import Dict, List, Optional
from config import GROK_API_KEY, GROK_API_URL, ERROR_MESSAGES, DEFAULT_LANGUAGE

class GrokAPIClient:
    """Client for interacting with Grok AI API"""
    
    def __init__(self, api_key: str = None, language: str = DEFAULT_LANGUAGE):
        self.api_key = api_key or GROK_API_KEY
        self.language = language
        self.base_url = GROK_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Make a request to the Grok AI API"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 1000) -> Optional[str]:
        """Generate a response using Grok AI"""
        try:
            # Prepare the prompt with context
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Add language instruction
            if self.language == "ru":
                full_prompt += "\n\nОтвечай на русском языке."
            else:
                full_prompt += "\n\nAnswer in English."
            
            data = {
                "model": "grok-beta",  # Adjust based on actual Grok model names
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            response = self._make_request("", data)
            if response and "choices" in response:
                return response["choices"][0]["message"]["content"]
            return None
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
    
    def generate_article(self, topic: str, language: str = None) -> Optional[str]:
        """Generate an article on a specific topic"""
        try:
            lang = language or self.language
            
            if lang == "ru":
                prompt = f"""Напиши интересную и информативную статью на тему "{topic}". 
                Статья должна быть:
                - Длиной 300-500 слов
                - Интересной для широкой аудитории
                - Содержать актуальную информацию
                - Хорошо структурированной
                
                Начни с заголовка и напиши полную статью."""
            else:
                prompt = f"""Write an interesting and informative article about "{topic}". 
                The article should be:
                - 300-500 words long
                - Engaging for a broad audience
                - Contain current information
                - Well-structured
                
                Start with a headline and write the complete article."""
            
            return self.generate_response(prompt, max_tokens=2000)
            
        except Exception as e:
            print(f"Error generating article: {e}")
            return None
    
    def answer_comment(self, comment: str, post_context: str = "", language: str = None) -> Optional[str]:
        """Generate a response to a user comment"""
        try:
            lang = language or self.language
            
            if lang == "ru":
                prompt = f"""Пользователь оставил комментарий: "{comment}"
                
                Контекст поста: {post_context if post_context else "Общий контекст"}
                
                Напиши вежливый, полезный и информативный ответ на этот комментарий. 
                Ответ должен быть:
                - Дружелюбным
                - Полезным
                - Не более 100 слов
                - На русском языке"""
            else:
                prompt = f"""A user left a comment: "{comment}"
                
                Post context: {post_context if post_context else "General context"}
                
                Write a polite, helpful, and informative response to this comment.
                The response should be:
                - Friendly
                - Helpful
                - No more than 100 words
                - In English"""
            
            return self.generate_response(prompt, max_tokens=500)
            
        except Exception as e:
            print(f"Error answering comment: {e}")
            return None
    
    def get_trending_topics(self, language: str = None) -> List[str]:
        """Get trending topics for article generation"""
        try:
            lang = language or self.language
            
            if lang == "ru":
                prompt = """Предложи 5 актуальных тем для статей, которые сейчас популярны в интернете. 
                Темы должны быть интересными и актуальными. 
                Верни только список тем, каждую с новой строки."""
            else:
                prompt = """Suggest 5 trending topics for articles that are currently popular on the internet.
                Topics should be interesting and relevant.
                Return only the list of topics, each on a new line."""
            
            response = self.generate_response(prompt, max_tokens=300)
            if response:
                topics = [topic.strip() for topic in response.split('\n') if topic.strip()]
                return topics[:5]  # Return max 5 topics
            
            return []
            
        except Exception as e:
            print(f"Error getting trending topics: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test the connection to Grok AI API"""
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'Connection successful'."
            response = self.generate_response(test_prompt, max_tokens=50)
            return response is not None and "successful" in response.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
