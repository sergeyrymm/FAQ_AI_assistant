# assistant.py
# Простой ассистент, который пока отвечает эхом
# Позже вы замените эту логику на вызов реального AI

def get_assistant_response(user_message: str) -> str:
    """
    Главная функция ассистента.
    Принимает сообщение от пользователя, возвращает ответ.
    """
    # Пока что просто эхо + эмодзи для красоты
    return f"🔊 Эхо: {user_message}"

# Дополнительная функция: ассистент может хранить историю диалога
# (опционально, для будущего использования)
class SimpleAssistant:
    def __init__(self):
        self.history = []
    
    def get_response(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        response = f"🤖 Вы сказали: {message}\n\n(Это временный ответ. Скоро здесь будет настоящий AI!)"
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def clear_history(self):
        self.history = []

# Создаём глобальный экземпляр для всего приложения (опционально)
assistant = SimpleAssistant()
