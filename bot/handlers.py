import threading
import time
from datetime import datetime, timedelta
from keybords import task_keyboard
from utils import state

# Создаем глобальный словарь для хранения задач
user_tasks = {}

# Функция для отправки напоминания
def send_task_reminder(bot, user_id, task):
    delay = (task['reminder_time'] - datetime.now()).total_seconds()
    time.sleep(max(0, delay))
    bot.send_message(
        user_id,
        f"⏰ Напоминание о задаче: \"{task['text']}\"!"
    )

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

            # Добавляем текст задачи в словарь со временем
            user_tasks[user_id].append({'text': task_text})

            # Запрос времени для установки напоминания
            state.add_state(user_id, "set_timer")
            bot.send_message(
                user_id,
                f"Задача \"{task_text}\" успешно добавлена!\nВведите время через сколько напомнить (в секундах):"
            )
        else:
            bot.send_message(
                user_id,
                "Текст задачи не может быть пустым. Пожалуйста, введите задачу:"
            )

    # Хендлер для установки времени напоминания
    @bot.message_handler(func=lambda msg: state.get_current_state(msg.chat.id) == "set_timer")
    def set_task_timer(message):
        user_id = message.chat.id
        try:
            delay = int(message.text)  # Получаем время в секундах
            if delay <= 0:
                raise ValueError("Время должно быть больше 0.")

            # Получаем последнюю добавленную задачу и обновляем со временем напоминания
            task = user_tasks[user_id][-1]
            task['reminder_time'] = datetime.now() + timedelta(seconds=delay)

            # Создаём новый поток для отправки напоминания
            threading.Thread(target=send_task_reminder, args=(bot, user_id, task)).start()

            # Возврат пользователя в главное меню
            state.add_state(user_id, "main")
            current_state = state.get_current_state(user_id)
            bot.send_message(
                user_id,
                f"⏳ Напоминание для задачи \"{task['text']}\" будет отправлено через {delay} секунд.",
                reply_markup=task_keyboard(current_state)
            )
        except ValueError:
            bot.send_message(
                user_id,

                "Введите корректное положительное число (в секундах):"
            )

    # Хендлер для отображения списка задач
    @bot.message_handler(func=lambda msg: msg.text == "Список задач")
    def list_tasks(message):
        user_id = message.chat.id
        state.add_state(user_id, "list_tasks")
        current_state = state.get_current_state(user_id)
        if user_id in user_tasks and user_tasks[user_id]:
            tasks_info = []
            for i, task in enumerate(user_tasks[user_id]):
                remaining_time = (task['reminder_time'] - datetime.now()).total_seconds()
                tasks_info.append(f"{i + 1}. {task['text']} - осталось {max(0, int(remaining_time))} секунд")

            bot.send_message(
                user_id,
                "Ваши задачи:\n" + "\n".join(tasks_info),
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
