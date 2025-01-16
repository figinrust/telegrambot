import time
from utils import state
from datetime import datetime, timedelta
import threading
from utils import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем глобальный словарь для хранения задач
user_tasks = {}

# Создаём глобальный словарь для хранения флагов завершения напоминаний
user_timers = {}

# Регистрация хендлеров для бота
def register_handler(bot):


    # Хендлер для команды /start
    @bot.message_handler(commands=["start"])
    def send_start_message(message):
        user_id = message.chat.id
        state.add_state(user_id, "start")
        current_state = state.get_current_state(user_id)

        logger.info(f"Пользователь {user_id} вызвал команду /start. Установлено состояние {current_state}")
        bot.send_message(
            user_id,
            "Бот напоминалка\nВот мои команды:\n"
            "/start - перезапуск\n"
            "/reset - сброс\n"
            "/add_task - добавление задачи\n"
            "/list - открыть список задачи\n"
            "/clear_task - удаление задач, время которых истекло",
        )
        logger.info(f'Словарь состояний - {state.user_states}')
        logger.info(f"Список задач {user_tasks}")
        logger.info((f"Список потоков {user_timers}"))

    # Хендлер для команды /reset
    @bot.message_handler(commands=["reset"])
    def reset_list(message):
        user_id = message.chat.id
        try:
            # Удаляем все задачи пользователя, если они существуют
            if user_id in user_tasks:
                user_tasks.pop(user_id)

            # Удаляем все флаги в user_timer
            if user_id in user_timers:
                user_timers.pop(user_id)

            # Очищаем состояния пользователя
            if user_id in state.user_states:
                state.user_states.pop(user_id)

            state.add_state(user_id, "start")
            current_state = state.get_current_state(user_id)

            logger.info(f"Пользователь {user_id} вызвал команду /reset. Установлено состояние {current_state}. Словарь user_tasks очищен - {user_tasks}")
            bot.send_message(user_id, "Сброс прошёл успешно")

            bot.send_message(
                user_id,
                "Вот мои команды:\n"
                "/start - перезапуск\n"
                "/reset - сброс\n"
                "/add_task - добавление задачи\n"
                "/list - открыть список задачи\n"
                "/clear_task - удаление задач, время которых истекло",
            )
        except ValueError as e:
            logger.error(f"Ошибка сброса {str(e)} {user_id}")
            bot.send_message(
                user_id,
                f"❌ Ошибка сброса."
            )


    # Хендлер для кнопки "Добавить задачу"
    @bot.message_handler(commands=["add_task"])
    def add_task(message):
        user_id = message.chat.id
        logger.info(f"Пользователь {user_id} начал добавление задачи.")
        state.add_state(user_id, "add_task")
        bot.send_message(
            user_id,
            "Введите текст задачи:"
        )

    # Хендлер для обработки введённого текста задачи
    @bot.message_handler(func=lambda msg: state.get_current_state(msg.chat.id) == "add_task")
    def save_task(message):
        user_id = message.chat.id
        task_text = message.text

        if task_text:
            if user_id not in user_tasks:
                user_tasks[user_id] = []

            user_tasks[user_id].append({'text': task_text})
            logger.info(f"Пользователь {user_id} добавил новую задачу: \"{task_text}\".")

            state.add_state(user_id, "set_timer")
            bot.send_message(
                user_id,
                f"Задача \"{task_text}\" успешно добавлена!\nВведите время через сколько напомнить в формате ЧЧ:ММ:СС:"
            )
        else:
            logger.warning(f"Пользователь {user_id} попытался добавить пустую задачу.")
            bot.send_message(
                user_id,
                "Текст задачи не может быть пустым. Пожалуйста, введите задачу:"
            )

    # Хендлер для установки времени напоминания
    @bot.message_handler(func=lambda msg: state.get_current_state(msg.chat.id) == "set_timer")
    def set_task_timer(message):
        user_id = message.chat.id
        try:
            time_parts = list(map(int, message.text.split(":")))
            if len(time_parts) != 3:
                raise ValueError("Введите корректное время в формате ЧЧ:ММ:СС.")

            hours, minutes, seconds = time_parts
            if hours < 0 or minutes < 0 or seconds < 0:
                raise ValueError("Значение времени не может быть отрицательным.")

            if minutes > 60 or seconds > 60:
                raise ValueError("Введите корректное значение минут или секунд")

            delay = hours * 3600 + minutes * 60 + seconds
            if delay <= 0:
                raise ValueError("Время должно быть больше 0.")

            task = user_tasks[user_id][-1]
            logger.info(f"{task} - последняя задача")
            task['reminder_time'] = datetime.now() + timedelta(seconds=delay)


            # Подготовка флага завершения
            stop_flag = threading.Event()
            user_timers[user_id] = stop_flag
            logger.info(f"Задача \"{task['text']}\" от пользователя {user_id} запланирована через {delay} секунд.")

            threading.Thread(target=send_task_reminder, args=(bot, user_id, task, stop_flag)).start()

            state.add_state(user_id, "main")
            bot.send_message(
                user_id,
                f"⏳ Напоминание для задачи \"{task['text']}\" будет отправлено через {hours}ч {minutes}м {seconds}с."
            )
        except ValueError as e:
            logger.error(f"Ошибка ввода времени {str(e)} от пользователя {user_id}: {e}")
            bot.send_message(
                user_id,
                f"❌ Ошибка. Введите время в формате ЧЧ:ММ:СС."
            )

    # Функция для отправки напоминаний
    def send_task_reminder(bot, user_id, task, stop_flag):
        delay = (task['reminder_time'] - datetime.now()).total_seconds()
        if stop_flag.wait(timeout=delay):
            return  # Были прекращены
        if delay <= 0:
            logger.warning(f"Напоминание для задачи \"{task['text']}\" пользователя {user_id} просрочено.")
            return

        logger.info(f"Отправка напоминания запланирована через {delay:.2f} секунд для пользователя {user_id}.")
        time.sleep(max(0, delay))
        bot.send_message(
            user_id,
            f"⏰ Напоминание о задаче: \"{task['text']}\"!"
        )
        logger.info(f"Напоминание отправлено пользователю {user_id} для задачи: \"{task['text']}\".")

    # Список задач
    @bot.message_handler(commands=["list"])
    def list_tasks(message):
        user_id = message.chat.id
        state.add_state(user_id, "list_tasks")

        if user_id in user_tasks and user_tasks[user_id]:
            tasks_info = []

            keyboard = InlineKeyboardMarkup()

            for i, task in enumerate(user_tasks[user_id]):
                try:
                    # Рассчёт оставшегося времени в секундах
                    remaining_time = max(0, int((task['reminder_time'] - datetime.now()).total_seconds()))

                    # Преобразование секунд в ЧЧ:ММ:СС
                    hours = remaining_time // 3600
                    minutes = (remaining_time % 3600) // 60
                    seconds = remaining_time % 60
                    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"


                    # Формируем строку с задачей
                    tasks_info.append(f"{i + 1}. {task["text"]} - осталось {formatted_time}")

                    # Добавляем кнопку для удаления задачи
                    button = InlineKeyboardButton(
                        f"Удалить задачу {i + 1}",
                        callback_data=f"delete_task_{i}"
                    )
                    keyboard.add(button)

                except Exception as e:
                    logger.error(f"Ошибка при обработке задачи: {e}")

            # Отправка списка задач пользователю
            bot.send_message(
                user_id,
                "Ваши задачи:\n" + "\n".join(tasks_info), reply_markup=keyboard
            )
        else:
            bot.send_message(
                user_id,
                "У вас пока нет задач."
            )

    # Очистка просроченных задач
    @bot.message_handler(commands=["clear_task"])
    def clear_task(message):
        user_id = message.chat.id

        # Проверяем наличие задач у пользователя
        if user_id not in user_tasks or not user_tasks[user_id]:
            bot.send_message(user_id, "У вас нет задач для очистки.")
            return  # Завершаем выполнение функции

        tasks_to_clear = []

        # Перебор всех задач пользователя и добавление просроченных в список на удаление
        for i, task in enumerate(user_tasks[user_id]):
            try:
                remaining_time = (task['reminder_time'] - datetime.now()).total_seconds()
                logger.info(f"{remaining_time} - время которое проверяется")
                if remaining_time <= 0:  # Если задача просрочена, помечаем на удаление
                    tasks_to_clear.append(i)
                    logger.info(f"Задача под индексом {tasks_to_clear[i]} помечена пользователем {user_id} на удаление")
            except Exception as e:
                print(f"Ошибка при проверке задачи {i + 1}: {e}")

        # Проверяем, есть ли задачи для удаления
        if tasks_to_clear:
            for index in reversed(tasks_to_clear):  # Удаляем задачи с конца списка
                deleted_task = user_tasks[user_id].pop(index)
                logger.info(f"Задача '{deleted_task['text']}' удалена, так как время истекло.")
                bot.send_message(
                    user_id, f"Задача '{deleted_task['text']}' удалена, так как время истекло."
                )

            logger.info(f"Все просроченные задачи пользователя {user_id} удалены")
            bot.send_message(user_id, "Все просроченные задания удалены.")
        else:
            logger.info(f"Нет задач с истекшим временем у пользователя {user_id}")
            bot.send_message(user_id, "Нет задач с истекшим временем.")

    # Удаление задач
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))
    def delete_task(call):
        try:
            # Получаем user_id через chat.id или from_user.id
            user_id = call.message.chat.id if call.message else call.from_user.id
            logger.info(f"Обработка запроса удаления задачи: {call.data}")

            if user_id in user_tasks and user_tasks[user_id]:
                # Извлекаем индекс задачи из callback_data
                task_index = int(call.data.split("_")[-1])  # Получаем индекс из callback_data
                if 0 <= task_index < len(user_tasks[user_id]):
                    deleted_task = user_tasks[user_id].pop(task_index)
                    user_timers[user_id].set()
                    logger.info("Таймер остановлен")
                    bot.send_message(user_id, f"Задача {task_index + 1} '{deleted_task['text']}' удалена.")
                    bot.answer_callback_query(call.id, text=f"Задача {task_index + 1} удалена.")
                    logger.info(f"Задача {task_index + 1} '{deleted_task['text']}' удалена.")
                else:
                    logger.warning(f"Некорректный индекс задачи: {task_index}")
                    bot.answer_callback_query(call.id, text="Некорректный индекс задачи.")
            else:
                logger.warning("Попытка удаления задачи у пользователя без задач.")
                bot.answer_callback_query(call.id, text="У вас нет задач для удаления.")
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи: {e}")
            bot.answer_callback_query(call.id, text="Ошибка удаления задачи!")