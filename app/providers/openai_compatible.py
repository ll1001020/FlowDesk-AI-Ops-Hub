from typing import List, Mapping
import requests
from .base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 45):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str, context: List[Mapping[str, str]]) -> str:
        if not self.base_url or not self.api_key:
            raise RuntimeError("LLM_BASE_URL and LLM_API_KEY are required for openai_compatible provider")
        context_text = "\n\n".join(f"[{i+1}] {c['source']} / {c['section']}\n{c['content']}" for i, c in enumerate(context))
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"问题：{user_prompt}\n\n检索上下文：\n{context_text}"},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
