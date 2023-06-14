from aiogram import Bot, Dispatcher, types, executor
from config import tg_bot_token
from googletrans import Translator
from aiogram.types import Message
from langdetect import detect

# Создаем переводчик
translator = Translator()

# Задаем исходные язык и целевой язык
src = 'en'
dest = 'ru'

# Задаем исходный текст
#text = 'Hello, how are you?'

# Переводим текст
#translated_text = translator.translate(text, src=src, dest=dest).text

bot = Bot(tg_bot_token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def on_message(message: types.Message):
    await bot.send_message(message.from_user.id, f"Hello {message.from_user.first_name}!")
    
@dp.message_handler(commands=['discuss'])
async def on_question(message: types.Message):
    await bot.send_message(message.from_user.id, f"Hello {message.from_user.first_name}! What discuss do you want?")
    
@dp.message_handler(commands=['translate'])
async def on_translation(message: types.Message):
    await bot.send_message(message.from_user.id, f"Hello {message.from_user.first_name}! Enter your text in english here >>>")
    
    @dp.message_handler()  
    async def text_translate(message: Message):
        src = detect(message.text)
        dest = 'ru'
        translated_text = translator.translate(message['text'], src=src, dest=dest).text        
        await bot.send_message(message.from_user.id, translated_text)
    #await bot.send_animation(message.from_user.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)