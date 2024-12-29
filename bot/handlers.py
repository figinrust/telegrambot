from keybords import task_keyboard
from utils import state

# Создаём глобальный словарь для хранения задач
user_tasks = {}


def register_handler(bot):
    # Хендлер для команды /start
    @bot.message_handler(commands=["start"])
    def send_start_message(message):
        user_id = message.chat.id
        state.add_state(user_id, "main")
        current_state = state.get_current_state(user_id)
        bot.send_message(
            user_id,
            "Бот напоминалка\nВот мои команды:",
            reply_markup=task_keyboard(current_state)
        )

    # Хендлер для кнопки "Добавить задачу"
    @bot.message_handler(func=lambda msg: msg.text == "Добавить задачу")
    def add_task(message):
        user_id = message.chat.id
        state.add_state(user_id, "add_task")
        current_state = state.get_current_state(user_id)
        bot.send_message(
            user_id,
            "Введите текст задачи:",
            reply_markup=task_keyboard(current_state)
        )

    # Хендлер для обработки введённого текста задачи
    @bot.message_handler(func=lambda msg: state.get_current_state(msg.chat.id) == "add_task")
    def save_task(message):
        user_id = message.chat.id
        task_text = message.text  # Текст задачи из сообщения

        if task_text:  # Проверяем, что текст непустой
            # Добавляем задачу в глобальный словарь
            if user_id not in user_tasks:
                user_tasks[user_id] = []  # Создаём список задач для пользователя
            user_tasks[user_id].append(task_text)  # Сохраняем задачу для пользователя

            # Возврат пользователя в главное меню
            state.add_state(user_id, "main")
            current_state = state.get_current_state(user_id)
            bot.send_message(
                user_id,
                f"Задача \"{task_text}\" успешно добавлена!",
                reply_markup=task_keyboard(current_state)
            )
        else:
            bot.send_message(
                user_id,
                "Текст задачи не может быть пустым. Пожалуйста, введите задачу:"
            )

    @bot.message_handler(func=lambda msg: msg.text == "Список задач")
    def list_tasks(message):
        user_id = message.chat.id
        state.add_state(user_id, "list_tasks")
        current_state = state.get_current_state(user_id)
        if user_id in user_tasks and user_tasks[user_id]:
            tasks = "\n".join([f"{i + 1}. {task}" for i, task in enumerate(user_tasks[user_id])])
            bot.send_message(
                user_id,
                f"Ваши задачи:\n{tasks}",
                reply_markup=task_keyboard(current_state)
            )
        else:
            bot.send_message(
                user_id,
                "У вас пока нет задач.",
                reply_markup=task_keyboard(current_state)
            )

    @bot.message_handler(func=lambda msg: msg.text == "Назад")
    def back_main(message):
        user_id = message.chat.id
        state.add_state(user_id, "main")
        current_state = state.get_current_state(user_id)
        bot.send_message(
            user_id,
            "Бот напоминалка\nВот мои команды:",
            reply_markup=task_keyboard(current_state)
        )