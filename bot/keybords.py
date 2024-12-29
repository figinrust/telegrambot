from telebot import types

def task_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("➕ Добавить задачу", "📋 Список задач")
    return keyboard
