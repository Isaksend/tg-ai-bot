import httpx
import logging
from typing import List, Dict
from app.config import config


class LLMManager:
    def __init__(self):
        self.url = f"{config.OLLAMA_URL}/api/chat"
        self.model = config.MODEL_NAME
        self.system_prompt = "Ты полезный AI-ассистент..."  # Из ТЗ [cite: 79]
        # Хранилище контекста в памяти: {user_id: [messages]} [cite: 16]
        self.history: Dict[int, List[Dict[str, str]]] = {}

    async def get_response(self, user_id: int, user_text: str) -> str:
        """Отправляет запрос в LLM с учетом истории диалога"""
        if user_id not in self.history:
            self.history[user_id] = [{"role": "system", "content": self.system_prompt}]

        # Добавляем сообщение пользователя в историю
        self.history[user_id].append({"role": "user", "content": user_text})

        # Ограничиваем контекст (MAX_CONTEXT_MESSAGES * 2 для учета пар вопрос-ответ + системный промпт) [cite: 39, 80]
        limit = config.MAX_CONTEXT_MESSAGES * 2
        if len(self.history[user_id]) > limit + 1:
            self.history[user_id] = [self.history[user_id][0]] + self.history[user_id][-(limit):]

        payload = {
            "model": self.model,
            "messages": self.history[user_id],
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:  # Таймаут для тяжелых моделей [cite: 82, 111]
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                result = response.json()

                ai_message = result['message']['content']

                # Сохраняем ответ бота в историю
                self.history[user_id].append({"role": "assistant", "content": ai_message})
                return ai_message

        except Exception as e:
            logging.error(f"Ollama error: {e}")
            return "Извини, я не смог обработать запрос к LLM."

    def reset_context(self, user_id: int):
        """Сброс истории диалога для пользователя """
        if user_id in self.history:
            self.history[user_id] = [{"role": "system", "content": self.system_prompt}]