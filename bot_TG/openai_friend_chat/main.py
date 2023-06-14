import os
import openai #импортируем библиотеку openai
import telebot #импортируем библиотеку для бота телеграм
from config import tg_bot_token, open_ai_token #берем переменные из локального файла config.py

#openai.api_key = os.getenv("OPENAI_API_KEY") #берем переменные из переменных окружения ОС
openai.api_key = open_ai_token  #переопределяем переменную с токеном openai

bot = telebot.TeleBot(tg_bot_token) #передаем переменную с токеном бота в телебот

@bot.message_handler(func=lambda _: True) #не знаю как работает лямбда эта)
def handle_message(message):             #создаем функцию с аргументом message
    response = openai.Completion.create(      #начинается кусок кода общения с openai, создает переменную response с ответом нейросети
        #model="text-davinci-003",          # имя модели openai, можно посмотреть в документации https://platform.openai.com/docs/introduction
        model="gpt-3.5-turbo",
        prompt=message.text,               #строка сходящего текста (то что бот получает от пользователя и отправляет нейросети)
        temperature=0.5,                   #хз, что-то openaiшное
        max_tokens=600,                     #хз
        top_p=1.0,                          #хз
        frequency_penalty=0.5,             #хз
        presence_penalty=0.0                #хз
    )
    bot.send_message(chat_id=message.from_user.id, text=response['choices'][0]['text']) 
    #дает команду боту отправить полученное от нейросети сообщение в чат с пользователем, 
    #указанным в chat_id, отправляет ответ
    #из переменной responce, парсит из всего ответа только текст самого ответа  
     
bot.polling()            
#бесконечно выполняющийся цикл запросов к серверам Telegram, 
#что не очень правильно в плане потребления ресурсов на обеих сторонах
#здесь лучше придумать что-то другое конечно

