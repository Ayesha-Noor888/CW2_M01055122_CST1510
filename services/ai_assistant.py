# services/ai_assistant.py

from typing import List, Dict


class AIAssistant:
    """
    Simple wrapper around an AI/chat model.

    In the real system this would call the OpenAI or Gemini API.
    Here we keep it simple and just echo the user input so the
    architecture is clear.
    """

    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []

    def set_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt

    def send_message(self, user_message: str) -> str:
        """
        Fake response for demo purposes.
        Replace this with a real API call if credits are available.
        """
        self._history.append({"role": "user", "content": user_message})

        response = f"[AI demo reply]: I received: {user_message[:80]}"
        self._history.append({"role": "assistant", "content": response})

        return response

    def clear_history(self) -> None:
        self._history.clear()
