def register_handlers(bot):
    from keybords import main_menu  # Импортируем функцию создания клавиатуры

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        # Создаём клавиатуру
        markup = main_menu()
        # Отправляем сообщение с клавиатурой
        bot.reply_to(message, "Добро пожаловать! Напишите /help для списка команд.", reply_markup=markup)

    @bot.message_handler(commands=['help'])
    def send_help(message):
        # Создаём клавиатуру
        markup = main_menu()
        # Отправляем сообщение с клавиатурой
        bot.reply_to(message, "Это помощь! Используйте команды /start и /help.", reply_markup=markup)

    @bot.message_handler(commands=['info'])
    def send_info(message):
        # Обработчик для кнопки "Информация"
        markup = main_menu()
        bot.reply_to(message, "Это информация о боте.", reply_markup=markup)
