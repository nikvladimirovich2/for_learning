from config import tg_bot_token  #library for token
from pycoingecko import CoinGeckoAPI  #library for coingecko
from telebot import TeleBot   #library for tg_bot

api = CoinGeckoAPI()  #rename method
bot = TeleBot(token=tg_bot_token)  #rename bot whit token
base_currency = "usd"  #var with currency

@bot.message_handler(content_types=['text'])  
def crypto_price_message_handler(message):
    crypto_id = message.text.lower()
    # list = print(api.get_coins_list())
    price = api.get_price(ids=crypto_id, vs_currencies=base_currency)
    
    if price:
        price = price[crypto_id][base_currency]
    else:
        bot.send_message(message.chat.id, f"Crypto {crypto_id} wasn't found")
        return

    bot.send_message(message.chat.id, f"Price of {crypto_id}={price} $")

if __name__ == '__main__':
    bot.polling()

