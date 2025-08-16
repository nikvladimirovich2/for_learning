import asyncio
import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, DEFAULT_LANGUAGE, ERROR_MESSAGES
from grok_api import GrokAPIClient
from channel_manager import ChannelManager
from comment_handler import CommentHandler
from article_generator import ArticleGenerator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GrokAdminBot:
    """Main Telegram bot class with Grok AI integration"""
    
    def __init__(self, token: str, language: str = DEFAULT_LANGUAGE):
        self.token = token
        self.language = language
        self.bot = Bot(token=token)
        
        # Initialize components
        self.grok_client = GrokAPIClient(language=language)
        self.channel_manager = ChannelManager(self.bot, language=language)
        self.comment_handler = CommentHandler(self.bot, self.grok_client, language=language)
        self.article_generator = ArticleGenerator(self.bot, self.grok_client, self.channel_manager, language=language)
        
        # Initialize application
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("generate_article", self.generate_article_command))
        self.application.add_handler(CommandHandler("generate_trending", self.generate_trending_command))
        self.application.add_handler(CommandHandler("post_article", self.post_article_command))
        self.application.add_handler(CommandHandler("channel_info", self.channel_info_command))
        self.application.add_handler(CommandHandler("comment_stats", self.comment_stats_command))
        self.application.add_handler(CommandHandler("article_stats", self.article_stats_command))
        self.application.add_handler(CommandHandler("schedule_articles", self.schedule_articles_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("test_grok", self.test_grok_command))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            welcome_message = self.get_welcome_message(user.first_name)
            
            keyboard = [
                [InlineKeyboardButton("📰 Сгенерировать статью", callback_data="generate_article")],
                [InlineKeyboardButton("🔥 Трендовые темы", callback_data="trending_topics")],
                [InlineKeyboardButton("📊 Статистика", callback_data="statistics")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            help_text = self.get_help_text()
            await update.message.reply_text(help_text, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Check Grok AI connection
            grok_status = self.grok_client.test_connection()
            
            # Get basic statistics
            comment_stats = self.comment_handler.get_comment_analytics()
            article_stats = self.article_generator.get_article_statistics()
            
            status_text = f"🤖 <b>Статус бота:</b>\n\n"
            status_text += f"🔗 <b>Grok AI:</b> {'✅ Подключен' if grok_status else '❌ Ошибка подключения'}\n"
            status_text += f"💬 <b>Комментарии обработано:</b> {comment_stats.get('total_comments_processed', 0)}\n"
            status_text += f"📰 <b>Статей сгенерировано:</b> {article_stats.get('total_generated', 0)}\n"
            status_text += f"🌐 <b>Язык:</b> {self.language.upper()}\n"
            
            await update.message.reply_text(status_text, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def generate_article_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate_article command"""
        try:
            if not context.args:
                await update.message.reply_text("Пожалуйста, укажите тему для статьи. Например: /generate_article искусственный интеллект")
                return
            
            topic = " ".join(context.args)
            await update.message.reply_text(f"🔄 Генерирую статью на тему: {topic}")
            
            # Generate article
            article_id = await self.article_generator.generate_article_on_topic(topic, self.language)
            
            if article_id:
                article_data = self.article_generator.get_article_by_id(article_id)
                content = article_data["content"]
                
                # Truncate if too long
                if len(content) > 4000:
                    content = content[:4000] + "..."
                
                keyboard = [
                    [InlineKeyboardButton("📤 Опубликовать в канале", callback_data=f"post_{article_id}")],
                    [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{article_id}")],
                    [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{article_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(f"📰 <b>Статья сгенерирована!</b>\n\n{content}", 
                                              reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text("❌ Ошибка при генерации статьи. Попробуйте позже.")
                
        except Exception as e:
            logger.error(f"Error in generate_article command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def generate_trending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate_trending command"""
        try:
            await update.message.reply_text("🔄 Генерирую статью на трендовую тему...")
            
            article_id = await self.article_generator.generate_trending_article(self.language)
            
            if article_id:
                article_data = self.article_generator.get_article_by_id(article_id)
                content = article_data["content"]
                topic = article_data["topic"]
                
                # Truncate if too long
                if len(content) > 4000:
                    content = content[:4000] + "..."
                
                keyboard = [
                    [InlineKeyboardButton("📤 Опубликовать в канале", callback_data=f"post_{article_id}")],
                    [InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_{article_id}")],
                    [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{article_id}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(f"🔥 <b>Трендовая статья: {topic}</b>\n\n{content}", 
                                              reply_markup=reply_markup, parse_mode='HTML')
            else:
                await update.message.reply_text("❌ Ошибка при генерации трендовой статьи. Попробуйте позже.")
                
        except Exception as e:
            logger.error(f"Error in generate_trending command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def post_article_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post_article command"""
        try:
            if not context.args:
                await update.message.reply_text("Пожалуйста, укажите ID статьи и ID канала. Например: /post_article article_123 channel_456")
                return
            
            if len(context.args) < 2:
                await update.message.reply_text("Необходимо указать ID статьи и ID канала")
                return
            
            article_id = context.args[0]
            channel_id = context.args[1]
            
            await update.message.reply_text(f"📤 Публикую статью {article_id} в канал {channel_id}...")
            
            success = await self.article_generator.post_article_to_channel(article_id, channel_id)
            
            if success:
                await update.message.reply_text("✅ Статья успешно опубликована в канале!")
            else:
                await update.message.reply_text("❌ Ошибка при публикации статьи")
                
        except Exception as e:
            logger.error(f"Error in post_article command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def channel_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /channel_info command"""
        try:
            if not context.args:
                await update.message.reply_text("Пожалуйста, укажите ID канала. Например: /channel_info @channel_name")
                return
            
            channel_id = context.args[0]
            channel_info = await self.channel_manager.get_channel_info(channel_id)
            
            if channel_info:
                info_text = f"📊 <b>Информация о канале:</b>\n\n"
                info_text += f"📝 <b>Название:</b> {channel_info['title']}\n"
                info_text += f"🔗 <b>Username:</b> @{channel_info['username']}\n"
                info_text += f"👥 <b>Тип:</b> {channel_info['type']}\n"
                if channel_info['member_count']:
                    info_text += f"👤 <b>Участников:</b> {channel_info['member_count']}\n"
                
                await update.message.reply_text(info_text, parse_mode='HTML')
            else:
                await update.message.reply_text("❌ Не удалось получить информацию о канале")
                
        except Exception as e:
            logger.error(f"Error in channel_info command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def comment_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /comment_stats command"""
        try:
            stats = self.comment_handler.get_comment_analytics()
            
            stats_text = f"💬 <b>Статистика комментариев:</b>\n\n"
            stats_text += f"📊 <b>Всего обработано:</b> {stats.get('total_comments_processed', 0)}\n"
            stats_text += f"👥 <b>Уникальных пользователей:</b> {stats.get('unique_users', 0)}\n"
            
            await update.message.reply_text(stats_text, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in comment_stats command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def article_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /article_stats command"""
        try:
            stats = self.article_generator.get_article_statistics()
            
            stats_text = f"📰 <b>Статистика статей:</b>\n\n"
            stats_text += f"📊 <b>Всего сгенерировано:</b> {stats.get('total_generated', 0)}\n"
            stats_text += f"📤 <b>Опубликовано:</b> {stats.get('total_posted', 0)}\n"
            stats_text += f"📈 <b>Процент публикации:</b> {stats.get('posting_rate', '0%')}\n"
            stats_text += f"⏰ <b>Активных расписаний:</b> {stats.get('active_schedules', 0)}\n"
            
            await update.message.reply_text(stats_text, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error in article_stats command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def schedule_articles_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /schedule_articles command"""
        try:
            if not context.args:
                await update.message.reply_text("Пожалуйста, укажите интервал в часах. Например: /schedule_articles 24")
                return
            
            try:
                interval = int(context.args[0])
                if interval < 1 or interval > 168:  # Max 1 week
                    await update.message.reply_text("Интервал должен быть от 1 до 168 часов")
                    return
            except ValueError:
                await update.message.reply_text("Интервал должен быть числом")
                return
            
            await update.message.reply_text(f"⏰ Настраиваю генерацию статей каждые {interval} часов...")
            
            success = await self.article_generator.schedule_article_generation(interval)
            
            if success:
                await update.message.reply_text(f"✅ Расписание настроено! Статьи будут генерироваться каждые {interval} часов")
            else:
                await update.message.reply_text("❌ Ошибка при настройке расписания")
                
        except Exception as e:
            logger.error(f"Error in schedule_articles command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        try:
            if not context.args:
                current_lang = "Русский" if self.language == "ru" else "English"
                await update.message.reply_text(f"🌐 <b>Текущий язык:</b> {current_lang}\n\n"
                                              f"Доступные языки: ru, en\n"
                                              f"Использование: /language ru", parse_mode='HTML')
                return
            
            new_language = context.args[0].lower()
            if new_language not in ["ru", "en"]:
                await update.message.reply_text("❌ Поддерживаются только языки: ru, en")
                return
            
            self.language = new_language
            self.grok_client.language = new_language
            self.channel_manager.language = new_language
            self.comment_handler.language = new_language
            self.article_generator.language = new_language
            
            lang_name = "Русский" if new_language == "ru" else "English"
            await update.message.reply_text(f"✅ Язык изменен на: {lang_name}")
            
        except Exception as e:
            logger.error(f"Error in language command: {e}")
            await update.message.reply_text(self.get_error_message("api_error"))
    
    async def test_grok_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test_grok command"""
        try:
            await update.message.reply_text("🔗 Тестирую подключение к Grok AI...")
            
            success = self.grok_client.test_connection()
            
            if success:
                await update.message.reply_text("✅ Подключение к Grok AI успешно!")
            else:
                await update.message.reply_text("❌ Ошибка подключения к Grok AI. Проверьте API ключ.")
                
        except Exception as e:
            logger.error(f"Error in test_grok command: {e}")
            await update.message.reply_text("❌ Ошибка при тестировании подключения")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            # Process comments if applicable
            await self.comment_handler.process_comment(update, context)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "generate_article":
                await query.edit_message_text("📝 Введите тему для статьи или используйте команду /generate_article <тема>")
                
            elif data == "trending_topics":
                await query.edit_message_text("🔥 Используйте команду /generate_trending для генерации статьи на трендовую тему")
                
            elif data == "statistics":
                await query.edit_message_text("📊 Используйте команды:\n/comment_stats - статистика комментариев\n/article_stats - статистика статей")
                
            elif data == "settings":
                await query.edit_message_text("⚙️ Используйте команды:\n/language - изменить язык\n/status - статус бота")
                
            elif data.startswith("post_"):
                article_id = data[5:]  # Remove "post_" prefix
                await query.edit_message_text(f"📤 Для публикации статьи {article_id} используйте команду:\n/post_article {article_id} <ID_канала>")
                
            elif data.startswith("edit_"):
                article_id = data[5:]  # Remove "edit_" prefix
                await query.edit_message_text(f"✏️ Для редактирования статьи {article_id} используйте команду:\n/edit_article {article_id} <новый_текст>")
                
            elif data.startswith("delete_"):
                article_id = data[7:]  # Remove "delete_" prefix
                await query.edit_message_text(f"🗑️ Статья {article_id} будет удалена при следующем перезапуске бота")
                
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            try:
                await query.edit_message_text("❌ Произошла ошибка при обработке запроса")
            except:
                pass
    
    def get_welcome_message(self, user_name: str) -> str:
        """Get localized welcome message"""
        if self.language == "ru":
            return f"👋 Привет, {user_name}!\n\nЯ бот-администратор с интеграцией Grok AI. Я могу:\n\n" \
                   f"📰 Генерировать статьи на популярные темы\n" \
                   f"💬 Отвечать на комментарии пользователей\n" \
                   f"📊 Управлять каналами Telegram\n\n" \
                   f"Используйте команду /help для получения справки."
        else:
            return f"👋 Hello, {user_name}!\n\nI'm an admin bot with Grok AI integration. I can:\n\n" \
                   f"📰 Generate articles on trending topics\n" \
                   f"💬 Respond to user comments\n" \
                   f"📊 Manage Telegram channels\n\n" \
                   f"Use /help command for assistance."
    
    def get_help_text(self) -> str:
        """Get localized help text"""
        if self.language == "ru":
            return """🤖 <b>Справка по командам:</b>

📰 <b>Генерация статей:</b>
/generate_article <тема> - создать статью на заданную тему
/generate_trending - создать статью на трендовую тему
/schedule_articles <часы> - настроить регулярную генерацию

📤 <b>Публикация:</b>
/post_article <ID_статьи> <ID_канала> - опубликовать статью

📊 <b>Статистика:</b>
/status - общий статус бота
/comment_stats - статистика комментариев
/article_stats - статистика статей
/channel_info <ID_канала> - информация о канале

⚙️ <b>Настройки:</b>
/language <ru/en> - изменить язык
/test_grok - проверить подключение к Grok AI

💬 <b>Автоматические функции:</b>
• Ответы на комментарии пользователей
• Модерация контента
• Управление каналами"""
        else:
            return """🤖 <b>Command Help:</b>

📰 <b>Article Generation:</b>
/generate_article <topic> - create article on specific topic
/generate_trending - create article on trending topic
/schedule_articles <hours> - set up regular generation

📤 <b>Publishing:</b>
/post_article <article_id> <channel_id> - publish article

📊 <b>Statistics:</b>
/status - general bot status
/comment_stats - comment statistics
/article_stats - article statistics
/channel_info <channel_id> - channel information

⚙️ <b>Settings:</b>
/language <ru/en> - change language
/test_grok - test Grok AI connection

💬 <b>Automatic Features:</b>
• Responding to user comments
• Content moderation
• Channel management"""
    
    def get_error_message(self, error_type: str) -> str:
        """Get localized error message"""
        try:
            return ERROR_MESSAGES.get(self.language, ERROR_MESSAGES["en"]).get(error_type, "An error occurred")
        except:
            return "An error occurred"
    
    async def run(self):
        """Run the bot"""
        try:
            logger.info("Starting Grok Admin Bot...")
            
            # Test Grok AI connection
            if not self.grok_client.test_connection():
                logger.warning("Grok AI connection test failed. Bot will start but some features may not work.")
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Bot started successfully!")
            
            # Keep the bot running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            await self.application.stop()
            await self.application.shutdown()

async def main():
    """Main function"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set in environment variables")
        return
    
    bot = GrokAdminBot(TELEGRAM_BOT_TOKEN)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
