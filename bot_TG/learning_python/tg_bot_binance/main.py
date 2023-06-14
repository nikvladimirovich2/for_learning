from aiogram.types import Message
from config import tg_bot_token  #
from aiogram import Bot, executor, Dispatcher
from binance import AsyncClient   #
from binance.exceptions import BinanceAPIException

bot = Bot(tg_bot_token)  #rename bot whit token
dispatcher = Dispatcher(bot)  #rename method
binance_client = AsyncClient()  #var with currency

@dispatcher.message_handler()  
async def handle_coin_price(message: Message):
    coin_price = await binance_client.get_ticker(symbol=message.text)
    print(coin_price['lastPrice'])
    await message.reply(text=coin_price['lastPrice'])
    
if __name__ == '__main__':
    executor.start_polling(dispatcher)    
    # list = print(api.get_coins_list())
#     price = api.get_price(ids=crypto_id, vs_currencies=base_currency)
    
#     if price:
#         price = price[crypto_id][base_currency]
#     else:
#         bot.send_message(message.chat.id, f"Crypto {crypto_id} wasn't found")
#         return

#     bot.send_message(message.chat.id, f"Price of {crypto_id}={price} $")

# if __name__ == '__main__':
#     bot.polling()

