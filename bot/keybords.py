from telebot.types import BotCommand


def keyboards_bot(bot):
    keyboards = [
        BotCommand("start", "перезапуск"),
        BotCommand("add_task", "добавление задачи"),
        BotCommand("list", "список задач"),
        BotCommand("clear_task", "удаление просроченных задач"),
        BotCommand("reset", "сброс")
    ]

    return bot.set_my_commands(keyboards)