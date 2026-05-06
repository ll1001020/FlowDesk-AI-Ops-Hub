from typing import List, Mapping
import requests
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str, timeout: int = 90):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str, context: List[Mapping[str, str]]) -> str:
        context_text = "\n\n".join(f"[{i+1}] {c['source']} / {c['section']}\n{c['content']}" for i, c in enumerate(context))
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"问题：{user_prompt}\n\n检索上下文：\n{context_text}"},
            ],
            "options": {"temperature": 0.2},
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["message"]["content"]
