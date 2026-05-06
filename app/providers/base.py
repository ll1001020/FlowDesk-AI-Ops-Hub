from abc import ABC, abstractmethod
from typing import List, Mapping


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, context: List[Mapping[str, str]]) -> str:
        raise NotImplementedError
