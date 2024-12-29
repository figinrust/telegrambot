import telebot
from config import BOT_TOKEN
from handlers import register_handlers

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Регистрация обработчиков
register_handlers(bot)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
