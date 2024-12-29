from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def task_keyboard(state):
    # Создаём клавиатуру в зависимости от состояния
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if state == "main":
        keyboard.add("Добавить задачу")
        keyboard.add("Список задач")
    elif state == "add_task":
        keyboard.add("Список задач")
        keyboard.add("Назад")
    elif state == "list_tasks":
        keyboard.add("Назад")
    return keyboard