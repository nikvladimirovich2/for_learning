import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telegram import Bot, Message
from grok_api import GrokAPIClient
from channel_manager import ChannelManager
from config import DEFAULT_TOPICS, MAX_ARTICLE_LENGTH, DEFAULT_LANGUAGE

class ArticleGenerator:
    """Generates articles on trending topics using Grok AI"""
    
    def __init__(self, bot: Bot, grok_client: GrokAPIClient, 
                 channel_manager: ChannelManager, language: str = DEFAULT_LANGUAGE):
        self.bot = bot
        self.grok_client = grok_client
        self.channel_manager = channel_manager
        self.language = language
        self.generated_articles = {}  # Track generated articles
        self.topic_suggestions = DEFAULT_TOPICS.copy()
        self.article_schedule = {}  # Schedule for article posting
        
    async def generate_article_on_topic(self, topic: str, language: str = None) -> Optional[str]:
        """Generate an article on a specific topic"""
        try:
            lang = language or self.language
            
            # Generate article using Grok AI
            article = self.grok_client.generate_article(topic, lang)
            
            if article:
                # Store the generated article
                article_id = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.generated_articles[article_id] = {
                    "topic": topic,
                    "content": article,
                    "language": lang,
                    "generated_at": datetime.now().isoformat(),
                    "posted": False
                }
                
                return article_id
            
            return None
            
        except Exception as e:
            print(f"Error generating article on topic '{topic}': {e}")
            return None
    
    async def generate_trending_article(self, language: str = None) -> Optional[str]:
        """Generate an article on a trending topic"""
        try:
            # Get trending topics from Grok AI
            trending_topics = self.grok_client.get_trending_topics(language or self.language)
            
            if trending_topics:
                # Select the first trending topic
                selected_topic = trending_topics[0]
                return await self.generate_article_on_topic(selected_topic, language)
            else:
                # Fallback to default topics
                import random
                fallback_topic = random.choice(self.topic_suggestions)
                return await self.generate_article_on_topic(fallback_topic, language)
                
        except Exception as e:
            print(f"Error generating trending article: {e}")
            return None
    
    async def generate_multiple_articles(self, count: int = 3, language: str = None) -> List[str]:
        """Generate multiple articles on different topics"""
        try:
            article_ids = []
            
            # Get trending topics
            trending_topics = self.grok_client.get_trending_topics(language or self.language)
            
            # Use trending topics if available, otherwise use default topics
            topics_to_use = trending_topics if trending_topics else self.topic_suggestions
            
            # Generate articles for different topics
            for i in range(min(count, len(topics_to_use))):
                topic = topics_to_use[i]
                article_id = await self.generate_article_on_topic(topic, language)
                if article_id:
                    article_ids.append(article_id)
                
                # Add small delay between generations
                await asyncio.sleep(2)
            
            return article_ids
            
        except Exception as e:
            print(f"Error generating multiple articles: {e}")
            return []
    
    async def post_article_to_channel(self, article_id: str, channel_id: str) -> bool:
        """Post a generated article to a channel"""
        try:
            if article_id not in self.generated_articles:
                print(f"Article {article_id} not found")
                return False
            
            article_data = self.generated_articles[article_id]
            content = article_data["content"]
            topic = article_data["topic"]
            
            # Format the article for channel posting
            formatted_article = self.format_article_for_channel(content, topic, article_data["language"])
            
            # Post to channel
            message = await self.channel_manager.post_message(channel_id, formatted_article)
            
            if message:
                # Mark as posted
                self.generated_articles[article_id]["posted"] = True
                self.generated_articles[article_id]["posted_at"] = datetime.now().isoformat()
                self.generated_articles[article_id]["channel_id"] = channel_id
                self.generated_articles[article_id]["message_id"] = message.message_id
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error posting article to channel: {e}")
            return False
    
    def format_article_for_channel(self, content: str, topic: str, language: str) -> str:
        """Format article content for channel posting"""
        try:
            if language == "ru":
                header = f"📰 <b>Новая статья: {topic}</b>\n\n"
                footer = "\n\n#новости #статья #интересное #актуально"
            else:
                header = f"📰 <b>New Article: {topic}</b>\n\n"
                footer = "\n\n#news #article #interesting #trending"
            
            # Truncate content if too long
            if len(content) > MAX_ARTICLE_LENGTH:
                content = content[:MAX_ARTICLE_LENGTH-100] + "..."
            
            formatted = header + content + footer
            return formatted
            
        except Exception as e:
            print(f"Error formatting article: {e}")
            return content
    
    async def schedule_article_generation(self, interval_hours: int = 24, 
                                        channel_id: str = None) -> bool:
        """Schedule regular article generation"""
        try:
            schedule_id = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.article_schedule[schedule_id] = {
                "interval_hours": interval_hours,
                "channel_id": channel_id,
                "active": True,
                "next_generation": datetime.now() + timedelta(hours=interval_hours),
                "last_generated": None
            }
            
            print(f"Article generation scheduled with ID: {schedule_id}")
            return True
            
        except Exception as e:
            print(f"Error scheduling article generation: {e}")
            return False
    
    async def process_scheduled_articles(self) -> List[str]:
        """Process scheduled article generation"""
        try:
            generated_articles = []
            current_time = datetime.now()
            
            for schedule_id, schedule in self.article_schedule.items():
                if not schedule["active"]:
                    continue
                
                if schedule["next_generation"] <= current_time:
                    # Time to generate article
                    article_id = await self.generate_trending_article()
                    
                    if article_id:
                        generated_articles.append(article_id)
                        
                        # Update schedule
                        schedule["last_generated"] = current_time.isoformat()
                        schedule["next_generation"] = current_time + timedelta(hours=schedule["interval_hours"])
                        
                        # Post to channel if specified
                        if schedule["channel_id"]:
                            await self.post_article_to_channel(article_id, schedule["channel_id"])
            
            return generated_articles
            
        except Exception as e:
            print(f"Error processing scheduled articles: {e}")
            return []
    
    def get_article_statistics(self) -> Dict:
        """Get statistics about generated articles"""
        try:
            total_articles = len(self.generated_articles)
            posted_articles = sum(1 for article in self.generated_articles.values() if article.get("posted", False))
            
            # Group by language
            language_stats = {}
            for article in self.generated_articles.values():
                lang = article.get("language", "unknown")
                language_stats[lang] = language_stats.get(lang, 0) + 1
            
            # Group by topic
            topic_stats = {}
            for article in self.generated_articles.values():
                topic = article.get("topic", "unknown")
                topic_stats[topic] = topic_stats.get(topic, 0) + 1
            
            return {
                "total_generated": total_articles,
                "total_posted": posted_articles,
                "posting_rate": f"{(posted_articles/total_articles*100):.1f}%" if total_articles > 0 else "0%",
                "by_language": language_stats,
                "by_topic": topic_stats,
                "active_schedules": len([s for s in self.article_schedule.values() if s["active"]])
            }
            
        except Exception as e:
            print(f"Error getting article statistics: {e}")
            return {}
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get article data by ID"""
        return self.generated_articles.get(article_id)
    
    def search_articles(self, query: str) -> List[Tuple[str, Dict]]:
        """Search articles by content or topic"""
        try:
            results = []
            query_lower = query.lower()
            
            for article_id, article_data in self.generated_articles.items():
                content = article_data.get("content", "").lower()
                topic = article_data.get("topic", "").lower()
                
                if query_lower in content or query_lower in topic:
                    results.append((article_id, article_data))
            
            return results
            
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []
    
    async def edit_article(self, article_id: str, new_content: str) -> bool:
        """Edit an existing article"""
        try:
            if article_id not in self.generated_articles:
                return False
            
            article_data = self.generated_articles[article_id]
            article_data["content"] = new_content
            article_data["edited_at"] = datetime.now().isoformat()
            
            # Update in channel if already posted
            if article_data.get("posted", False) and "channel_id" in article_data and "message_id" in article_data:
                formatted_content = self.format_article_for_channel(
                    new_content, 
                    article_data["topic"], 
                    article_data["language"]
                )
                
                await self.channel_manager.edit_message(
                    article_data["channel_id"],
                    article_data["message_id"],
                    formatted_content
                )
            
            return True
            
        except Exception as e:
            print(f"Error editing article: {e}")
            return False
    
    def export_articles(self, format_type: str = "json") -> str:
        """Export articles in specified format"""
        try:
            if format_type == "json":
                return json.dumps(self.generated_articles, indent=2, ensure_ascii=False)
            elif format_type == "text":
                output = []
                for article_id, article_data in self.generated_articles.items():
                    output.append(f"=== {article_id} ===")
                    output.append(f"Topic: {article_data['topic']}")
                    output.append(f"Language: {article_data['language']}")
                    output.append(f"Generated: {article_data['generated_at']}")
                    output.append(f"Content:\n{article_data['content']}")
                    output.append("\n" + "="*50 + "\n")
                return "\n".join(output)
            else:
                return "Unsupported format"
                
        except Exception as e:
            print(f"Error exporting articles: {e}")
            return f"Export error: {e}"
