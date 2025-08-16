import asyncio
from typing import Dict, List, Optional, Tuple
from telegram import Bot, Update, Message, ChatMember
from telegram.ext import ContextTypes
from config import ADMIN_CHANNEL_ID, PUBLIC_CHANNEL_ID, ERROR_MESSAGES, DEFAULT_LANGUAGE

class ChannelManager:
    """Manages Telegram channel operations"""
    
    def __init__(self, bot: Bot, language: str = DEFAULT_LANGUAGE):
        self.bot = bot
        self.language = language
        self.admin_channel_id = ADMIN_CHANNEL_ID
        self.public_channel_id = PUBLIC_CHANNEL_ID
        
    async def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Get information about a channel"""
        try:
            chat = await self.bot.get_chat(channel_id)
            return {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "type": chat.type,
                "member_count": chat.member_count if hasattr(chat, 'member_count') else None
            }
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None
    
    async def post_message(self, channel_id: str, text: str, 
                          reply_to_message_id: int = None) -> Optional[Message]:
        """Post a message to a channel"""
        try:
            message = await self.bot.send_message(
                chat_id=channel_id,
                text=text,
                reply_to_message_id=reply_to_message_id,
                parse_mode='HTML'
            )
            return message
        except Exception as e:
            print(f"Error posting message: {e}")
            return None
    
    async def edit_message(self, channel_id: str, message_id: int, 
                          new_text: str) -> bool:
        """Edit a message in a channel"""
        try:
            await self.bot.edit_message_text(
                chat_id=channel_id,
                message_id=message_id,
                text=new_text,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            print(f"Error editing message: {e}")
            return False
    
    async def delete_message(self, channel_id: str, message_id: int) -> bool:
        """Delete a message from a channel"""
        try:
            await self.bot.delete_message(
                chat_id=channel_id,
                message_id=message_id
            )
            return True
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False
    
    async def pin_message(self, channel_id: str, message_id: int) -> bool:
        """Pin a message in a channel"""
        try:
            await self.bot.pin_chat_message(
                chat_id=channel_id,
                message_id=message_id
            )
            return True
        except Exception as e:
            print(f"Error pinning message: {e}")
            return False
    
    async def get_channel_messages(self, channel_id: str, limit: int = 10) -> List[Message]:
        """Get recent messages from a channel"""
        try:
            messages = []
            async for message in self.bot.get_chat_history(chat_id=channel_id, limit=limit):
                messages.append(message)
            return messages
        except Exception as e:
            print(f"Error getting channel messages: {e}")
            return []
    
    async def get_message_replies(self, channel_id: str, message_id: int) -> List[Message]:
        """Get replies to a specific message"""
        try:
            # This is a simplified approach - Telegram doesn't directly provide reply threads
            # You might need to implement a more sophisticated solution based on your needs
            messages = await self.get_channel_messages(channel_id, 50)
            replies = []
            for msg in messages:
                if hasattr(msg, 'reply_to_message') and msg.reply_to_message:
                    if msg.reply_to_message.message_id == message_id:
                        replies.append(msg)
            return replies
        except Exception as e:
            print(f"Error getting message replies: {e}")
            return []
    
    async def check_user_permissions(self, user_id: int, channel_id: str) -> Dict[str, bool]:
        """Check user permissions in a channel"""
        try:
            member = await self.bot.get_chat_member(channel_id, user_id)
            return {
                "can_post": member.can_post_messages if hasattr(member, 'can_post_messages') else False,
                "can_edit": member.can_edit_messages if hasattr(member, 'can_edit_messages') else False,
                "can_delete": member.can_delete_messages if hasattr(member, 'can_delete_messages') else False,
                "is_admin": member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR],
                "is_creator": member.status == ChatMember.CREATOR
            }
        except Exception as e:
            print(f"Error checking user permissions: {e}")
            return {
                "can_post": False,
                "can_edit": False,
                "can_delete": False,
                "is_admin": False,
                "is_creator": False
            }
    
    async def ban_user(self, channel_id: str, user_id: int, reason: str = "") -> bool:
        """Ban a user from a channel"""
        try:
            await self.bot.ban_chat_member(
                chat_id=channel_id,
                user_id=user_id,
                until_date=None  # Permanent ban
            )
            return True
        except Exception as e:
            print(f"Error banning user: {e}")
            return False
    
    async def unban_user(self, channel_id: str, user_id: int) -> bool:
        """Unban a user from a channel"""
        try:
            await self.bot.unban_chat_member(
                chat_id=channel_id,
                user_id=user_id
            )
            return True
        except Exception as e:
            print(f"Error unbanning user: {e}")
            return False
    
    async def get_channel_statistics(self, channel_id: str) -> Dict:
        """Get channel statistics"""
        try:
            chat = await self.bot.get_chat(channel_id)
            stats = {
                "title": chat.title,
                "username": chat.username,
                "member_count": getattr(chat, 'member_count', 'Unknown'),
                "description": getattr(chat, 'description', ''),
                "type": chat.type
            }
            return stats
        except Exception as e:
            print(f"Error getting channel statistics: {e}")
            return {}
    
    def format_message_for_channel(self, content: str, content_type: str = "text") -> str:
        """Format content for channel posting"""
        if content_type == "article":
            # Add formatting for articles
            return f"📰 <b>Новая статья</b>\n\n{content}\n\n#новости #статья #интересное"
        elif content_type == "announcement":
            # Add formatting for announcements
            return f"📢 <b>Объявление</b>\n\n{content}"
        else:
            return content
    
    async def schedule_post(self, channel_id: str, text: str, 
                           schedule_time: int) -> bool:
        """Schedule a post for later (simplified implementation)"""
        try:
            # This is a simplified scheduling - in production you'd want a proper scheduler
            await asyncio.sleep(schedule_time)
            await self.post_message(channel_id, text)
            return True
        except Exception as e:
            print(f"Error scheduling post: {e}")
            return False
