import datetime

# Пример структуры для хранения задач
tasks = {}

def add_task(user_id, task_text, task_time):
    if user_id not in tasks:
        tasks[user_id] = []
    tasks[user_id].append((task_text, task_time))

def get_tasks(user_id):
    if user_id in tasks:
        return tasks[user_id]
    return []