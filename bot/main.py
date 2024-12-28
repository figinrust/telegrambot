import telebot
from config import BOT_TOKEN
from handlers import register_handlers
from keybords import main_menu

bot = telebot.TeleBot(BOT_TOKEN)
# Регистрация обработчиков
register_handlers(bot)
bot.polling()  # Запуск бота
