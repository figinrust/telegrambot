import telebot
from telebot import types

def main_menu():
    # Создание объекта клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    # Добавление кнопок на клавиатуру
    button_start = types.KeyboardButton("/start")
    button_help = types.KeyboardButton("/help")
    button_info = types.KeyboardButton("/info")

    # Добавление кнопок на клавиатуру
    markup.add(button_start, button_help, button_info)

    return markup
