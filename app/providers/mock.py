from typing import List, Mapping
from .base import LLMProvider


class MockProvider(LLMProvider):
    def generate(self, system_prompt: str, user_prompt: str, context: List[Mapping[str, str]]) -> str:
        context_text = "\n".join(f"- {item['section']}: {item['content'][:140]}" for item in context)
        return (
            "基于已检索 SOP，建议先做现场止损，再做根因排查，最后按升级条件转人工/主管。\n\n"
            "可执行方案：\n"
            "1. 先确认是否影响交易、履约或安全，若影响多人或核心链路，立即升级为高优先级。\n"
            "2. 按知识库中的标准动作逐项排查，记录时间、设备编号、用户反馈和截图。\n"
            "3. 若 15 分钟内无法恢复，启用替代流程，避免业务继续堆积。\n"
            "4. 处理完成后，把根因、临时方案、最终方案写回工单。\n\n"
            f"参考依据：\n{context_text}"
        )
