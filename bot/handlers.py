import time
from utils import state
from datetime import datetime, timedelta
import threading
import logging

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
        bot.delete_my_commands()
        bot.set_my_commands([])
        user_id = message.chat.id
        state.add_state(user_id, "main")
        current_state = state.get_current_state(user_id)
        bot.send_message(
            user_id,
            "Бот напоминалка\nВот мои команды:\n/start - запуск меню\n/add_task - добавление задачи\n/list - открыть список задачи\n/clear_task - удаление задач время которых закончилось",
            reply_markup=None
        )

    # Хендлер для кнопки "Добавить задачу"
    @bot.message_handler(commands=["add_task"])
    def add_task(message):
        user_id = message.chat.id
        state.add_state(user_id, "add_task")
        current_state = state.get_current_state(user_id)
        bot.send_message(
            user_id,
            "Введите текст задачи:"
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
                f"Задача \"{task_text}\" успешно добавлена!\nВведите время через сколько напомнить в формате ЧЧ:ММ:СС. :"
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
            # Ожидаем ввод в формате "часы:минуты:секунды"
            time_parts = list(map(int, message.text.split(":")))

            if len(time_parts) != 3:
                raise ValueError("Введите корректное время в формате ЧЧ:ММ:СС.")

            hours, minutes, seconds = time_parts

            if hours < 0 or minutes < 0 or seconds < 0:
                raise ValueError("Значение времени не может быть отрицательным.")

            # Проверяем положительные значения
            if hours < 0 or minutes < 0 or seconds < 0:
                raise ValueError("Значение времени не может быть отрицательным.")

            # Преобразуем всё в секунды
            if minutes <= 60 and seconds <= 60:
                delay = hours * 3600 + minutes * 60 + seconds
            else:
                raise ValueError("Введите корректное значение минут или секунд")

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
                f"⏳ Напоминание для задачи \"{task['text']}\" будет отправлено через {hours}ч {minutes}м {seconds}с."
            )
        except ValueError as e:
            bot.send_message(
                user_id,
                f"❌ Ошибка: {str(e)}. Введите время в формате ЧЧ:ММ:СС."
            )

    # Хендлер для отображения списка задач
    @bot.message_handler(commands=["list"])
    def list_tasks(message):
        user_id = message.chat.id
        state.add_state(user_id, "list_tasks")
        current_state = state.get_current_state(user_id)

        if user_id in user_tasks and user_tasks[user_id]:
            tasks_info = []
            for i, task in enumerate(user_tasks[user_id]):
                # Рассчёт оставшегося времени в секундах
                remaining_time = max(0, int((task['reminder_time'] - datetime.now()).total_seconds()))

                # Преобразование секунд в ЧЧ:ММ:СС
                hours = remaining_time // 3600
                minutes = (remaining_time % 3600) // 60
                seconds = remaining_time % 60
                formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

                # Формируем строку с задачей
                tasks_info.append(f"{i + 1}. {task['text']} - осталось {formatted_time}")

            # Отправка списка задач пользователю
            bot.send_message(
                user_id,
                "Ваши задачи:\n" + "\n".join(tasks_info)
            )
        else:
            bot.send_message(
                user_id,
                "У вас пока нет задач."
            )

    @bot.message_handler(commands=["clear_task"])
    def delete_task(message):
        user_id = message.chat.id
        if user_id in user_tasks and user_tasks[user_id]:
            tasks_to_delete = []

            for i, task in enumerate(user_tasks[user_id]):
                remaining_time = (task['reminder_time'] - datetime.now()).total_seconds()
                if remaining_time <= 0:
                    tasks_to_delete.append(i)

            if tasks_to_delete:
                for index in reversed(tasks_to_delete):
                    deleted_task = user_tasks[user_id].pop(index)
                    bot.send_message(user_id, f"Задача '{deleted_task['text']}' удалена, так как время истекло.")

                bot.send_message(user_id, "Все просроченные задания удалены")

            else:
                bot.send_message(user_id, "Нет задач с истекшим временем.")
        else:
            bot.send_message(user_id, "У вас нет задач для очистки.")