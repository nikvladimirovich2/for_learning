import asyncio
from typing import Dict, List, Optional, Tuple
from telegram import Bot, Update, Message, User
from telegram.ext import ContextTypes
from chatgpt_api import ChatGPTAPIClient
from config import ERROR_MESSAGES, DEFAULT_LANGUAGE, MAX_COMMENT_LENGTH

class CommentHandler:
    """Handles user comments and generates AI-powered responses"""
    
    def __init__(self, bot: Bot, chatgpt_client: ChatGPTAPIClient, language: str = DEFAULT_LANGUAGE):
        self.bot = bot
        self.chatgpt_client = chatgpt_client
        self.language = language
        self.pending_comments = {}  # Track comments being processed
        self.comment_history = {}   # Store comment history for context
        
    async def process_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Process a new comment and generate a response"""
        try:
            if not update.message or not update.message.text:
                return False
                
            comment = update.message.text
            user = update.message.from_user
            chat_id = update.message.chat_id
            message_id = update.message.message_id
            
            # Check if this is a comment on a channel post
            if hasattr(update.message, 'reply_to_message') and update.message.reply_to_message:
                return await self.handle_reply_comment(update, context)
            
            # Check if this is a direct comment in a channel
            if update.message.chat.type in ['channel', 'supergroup']:
                return await self.handle_channel_comment(update, context)
            
            return False
            
        except Exception as e:
            print(f"Error processing comment: {e}")
            return False
    
    async def handle_reply_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle a reply comment to a channel post"""
        try:
            comment = update.message.text
            user = update.message.from_user
            original_message = update.message.reply_to_message
            chat_id = update.message.chat_id
            
            # Get context from the original message
            post_context = self.extract_post_context(original_message)
            
            # Generate AI response
            ai_response = await self.generate_comment_response(comment, post_context, user)
            
            if ai_response:
                # Reply to the comment
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=ai_response,
                    reply_to_message_id=update.message.message_id,
                    parse_mode='HTML'
                )
                
                # Store in history
                self.store_comment_history(user.id, comment, ai_response, post_context)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error handling reply comment: {e}")
            return False
    
    async def handle_channel_comment(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle a comment directly in a channel"""
        try:
            comment = update.message.text
            user = update.message.from_user
            chat_id = update.message.chat_id
            
            # Get recent channel context
            channel_context = await self.get_channel_context(chat_id)
            
            # Generate AI response
            ai_response = await self.generate_comment_response(comment, channel_context, user)
            
            if ai_response:
                # Reply to the comment
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=ai_response,
                    reply_to_message_id=update.message.message_id,
                    parse_mode='HTML'
                )
                
                # Store in history
                self.store_comment_history(user.id, comment, ai_response, channel_context)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error handling channel comment: {e}")
            return False
    
    async def generate_comment_response(self, comment: str, context: str, user: User) -> Optional[str]:
        """Generate an AI-powered response to a comment"""
        try:
            # Check comment length
            if len(comment) > MAX_COMMENT_LENGTH:
                return self.get_error_message("comment_too_long")
            
            # Add user context
            user_context = f"User: {user.first_name} {user.last_name or ''} (ID: {user.id})"
            full_context = f"{context}\n\n{user_context}"
            
            # Generate response using OpenAI ChatGPT
            response = self.chatgpt_client.answer_comment(comment, full_context, self.language)
            
            if response:
                # Format the response
                formatted_response = self.format_comment_response(response, user)
                return formatted_response
            
            return self.get_error_message("api_error")
            
        except Exception as e:
            print(f"Error generating comment response: {e}")
            return self.get_error_message("api_error")
    
    def extract_post_context(self, message: Message) -> str:
        """Extract context from a message for comment responses"""
        try:
            context_parts = []
            
            if message.text:
                context_parts.append(f"Post content: {message.text[:200]}...")
            
            if message.caption:
                context_parts.append(f"Post caption: {message.caption[:200]}...")
            
            if message.photo:
                context_parts.append("Post contains image")
            
            if message.video:
                context_parts.append("Post contains video")
            
            if message.document:
                context_parts.append("Post contains document")
            
            return " | ".join(context_parts) if context_parts else "General post context"
            
        except Exception as e:
            print(f"Error extracting post context: {e}")
            return "General post context"
    
    async def get_channel_context(self, chat_id: int) -> str:
        """Get recent context from a channel"""
        try:
            # Get recent messages for context
            messages = []
            async for message in self.bot.get_chat_history(chat_id=chat_id, limit=5):
                if message.text:
                    messages.append(message.text[:100])
            
            if messages:
                return f"Recent channel context: {' | '.join(messages)}"
            else:
                return "General channel context"
                
        except Exception as e:
            print(f"Error getting channel context: {e}")
            return "General channel context"
    
    def format_comment_response(self, response: str, user: User) -> str:
        """Format the AI response for better presentation"""
        try:
            # Add user mention if possible
            user_mention = f"@{user.username}" if user.username else user.first_name
            
            if self.language == "ru":
                formatted = f"💬 <b>Ответ от бота:</b>\n\n{response}\n\n— <i>С уважением, команда канала</i>"
            else:
                formatted = f"💬 <b>Bot response:</b>\n\n{response}\n\n— <i>Best regards, channel team</i>"
            
            return formatted
            
        except Exception as e:
            print(f"Error formatting comment response: {e}")
            return response
    
    def store_comment_history(self, user_id: int, comment: str, response: str, context: str):
        """Store comment history for future reference"""
        try:
            if user_id not in self.comment_history:
                self.comment_history[user_id] = []
            
            self.comment_history[user_id].append({
                "comment": comment,
                "response": response,
                "context": context,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Keep only last 10 comments per user
            if len(self.comment_history[user_id]) > 10:
                self.comment_history[user_id] = self.comment_history[user_id][-10:]
                
        except Exception as e:
            print(f"Error storing comment history: {e}")
    
    def get_user_comment_history(self, user_id: int) -> List[Dict]:
        """Get comment history for a specific user"""
        return self.comment_history.get(user_id, [])
    
    def get_error_message(self, error_type: str) -> str:
        """Get localized error message"""
        try:
            return ERROR_MESSAGES.get(self.language, ERROR_MESSAGES["en"]).get(error_type, "An error occurred")
        except:
            return "An error occurred"
    
    async def moderate_comment(self, comment: str, user: User) -> Tuple[bool, str]:
        """Moderate a comment for inappropriate content"""
        try:
            # Basic moderation using Grok AI
            moderation_prompt = f"""Please moderate this comment: "{comment}"
            
            Determine if this comment is:
            1. Appropriate and respectful
            2. Spam or promotional
            3. Offensive or inappropriate
            4. Relevant to the discussion
            
            Respond with only: APPROPRIATE, SPAM, OFFENSIVE, or IRRELEVANT"""
            
            moderation_result = self.chatgpt_client.generate_response(moderation_prompt, max_tokens=50)
            
            if moderation_result:
                result = moderation_result.strip().upper()
                if result in ["APPROPRIATE", "RELEVANT"]:
                    return True, "Comment approved"
                elif result == "SPAM":
                    return False, "Comment flagged as spam"
                elif result == "OFFENSIVE":
                    return False, "Comment flagged as offensive"
                else:
                    return False, "Comment flagged as irrelevant"
            
            # Default to approval if moderation fails
            return True, "Comment approved (moderation unavailable)"
            
        except Exception as e:
            print(f"Error moderating comment: {e}")
            return True, "Comment approved (moderation error)"
    
    async def get_comment_analytics(self) -> Dict:
        """Get analytics about comment handling"""
        try:
            total_comments = sum(len(history) for history in self.comment_history.values())
            unique_users = len(self.comment_history.keys())
            
            return {
                "total_comments_processed": total_comments,
                "unique_users": unique_users,
                "average_response_time": "N/A",  # Could implement timing tracking
                "success_rate": "N/A"  # Could implement success tracking
            }
            
        except Exception as e:
            print(f"Error getting comment analytics: {e}")
            return {}
