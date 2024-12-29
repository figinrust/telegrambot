from keybords import task_keyboard
from utils import add_task, get_tasks
from datetime import datetime, timedelta

# Бот инициализируется из main.py
bot = None

# Хранение состояний пользователей
user_states = {}

# Определение состояний
STATE_WAITING_FOR_TASK = "waiting_for_task"
STATE_WAITING_FOR_TIME = "waiting_for_time"

def register_handlers(main_bot):
    global bot
    bot = main_bot

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(
            message.chat.id,
            "Привет! Я помогу тебе с напоминаниями. Выбери действие:",
            reply_markup=task_keyboard()
        )

    @bot.message_handler(func=lambda msg: msg.text == "➕ Добавить задачу")
    def add_task_message(message):
        bot.send_message(message.chat.id, "Напиши текст задачи:")
        user_states[message.chat.id] = STATE_WAITING_FOR_TASK

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == STATE_WAITING_FOR_TASK)
    def task_text_handler(message):
        task_text = message.text
        bot.send_message(message.chat.id, "Через сколько минут напомнить? (Укажи число)")
        user_states[message.chat.id] = (STATE_WAITING_FOR_TIME, task_text)

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, (None,))[0] == STATE_WAITING_FOR_TIME)
    def task_time_handler(message):
        try:
            delay = int(message.text) * 60
            task_text = user_states[message.chat.id][1]
            task_time = datetime.now() + timedelta(seconds=delay)
            add_task(message.chat.id, task_text, task_time)
            bot.send_message(
                message.chat.id,
                f"✅ Задача добавлена! Я напомню тебе: \"{task_text}\" через {message.text} минут(ы).",
                reply_markup=task_keyboard()
            )
            user_states.pop(message.chat.id, None)  # Очистка состояния
        except ValueError:
            bot.send_message(message.chat.id, "❌ Ошибка: число времени некорректно. Попробуй снова.")

    @bot.message_handler(func=lambda msg: msg.text == "📋 Список задач")
    def list_tasks_message(message):
        user_tasks = get_tasks(message.chat.id)
        if user_tasks:
            tasks_text = []
            for task in user_tasks:
                task_text, task_time = task
                remaining_time = task_time - datetime.now()
                if remaining_time.total_seconds() > 0:
                    minutes, seconds = divmod(remaining_time.total_seconds(), 60)
                    tasks_text.append(f"- {task_text} (осталось {int(minutes)} минут и {int(seconds)} секунд)")
                else:
                    tasks_text.append(f"- {task_text} (время истекло)")
            tasks_message = "\n".join(tasks_text)
            bot.send_message(message.chat.id, f"📋 Твои задачи:\n{tasks_message}")
        else:
            bot.send_message(message.chat.id, "📭 У тебя нет задач.")