import telebot
from bot.handlers import register_handler
from config import BOT_TOKEN
from keybords import keyboards_bot

bot = telebot.TeleBot(BOT_TOKEN)
register_handler(bot)
keyboards_bot(bot)

if __name__ == "__main__":
    bot.polling(none_stop=True)

