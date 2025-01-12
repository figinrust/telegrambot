import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()   # Лог отображается в консоли
    ]
)

logger = logging.getLogger(__name__)  # Создаём объект логгера

class State:
    def __init__(self):
        self.user_states = {} # Словарь для хранения состояний

    def get_current_state(self, user_id):
        return self.user_states.get(user_id, [])[-1] if user_id in self.user_states and self.user_states[user_id] else None


    def add_state(self, user_id, state):
        if user_id not in self.user_states:
            self.user_states[user_id] = []
        self.user_states[user_id].append(state)

    def go_back(self, user_id):
        if user_id in self.user_states and len(self.user_states) > 1:
            self.user_states[user_id].pop()
        return self.get_current_state(user_id)

state = State()