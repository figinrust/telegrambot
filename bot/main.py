import telebot

from bot.handlers import register_handler
from config import BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)
register_handler(bot)

bot.polling()