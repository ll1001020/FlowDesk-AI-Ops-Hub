from typing import List, Tuple

from app.providers.base import LLMProvider
from app.rag import KnowledgeBase, SearchHit
from app.schemas import AssistResponse, Citation

HIGH_KEYWORDS = ["停机", "无法", "中断", "投诉", "安全", "漏水", "冒烟", "高温", "排队", "宕机", "丢失", "风险"]
MEDIUM_KEYWORDS = ["异常", "延迟", "报错", "失败", "卡顿", "签收", "退款", "超时", "温度"]

SCENARIO_OWNER = {
    "retail_ops": "门店运营/IT 支持",
    "ecommerce_support": "客服主管/履约团队",
    "campus_ops": "后勤维修/物业",
    "device_inspection": "设备运维/安全员",
    "general": "一线支持团队",
}


def classify_issue(text: str, scenario: str) -> Tuple[str, str, str]:
    normalized = text.lower()
    high_hits = sum(1 for word in HIGH_KEYWORDS if word in normalized)
    medium_hits = sum(1 for word in MEDIUM_KEYWORDS if word in normalized)
    if high_hits >= 2:
        severity = "P1 高优先级"
        sla = "15 分钟内响应，30 分钟内给出止损方案"
    elif high_hits == 1 or medium_hits >= 2:
        severity = "P2 中优先级"
        sla = "30 分钟内响应，2 小时内完成初步处理"
    else:
        severity = "P3 常规优先级"
        sla = "4 小时内响应，1 个工作日内处理"
    return severity, SCENARIO_OWNER.get(scenario, SCENARIO_OWNER["general"]), sla


def make_checklist(question: str, hits: List[SearchHit], severity: str) -> List[str]:
    checklist = [
        "确认影响范围：涉及人数、业务链路、设备编号、发生时间。",
        "先执行临时止损：切换备用流程、告知相关人员、保留现场证据。",
        "按知识库引用步骤逐项排查，并记录每一步结果。",
    ]
    if "P1" in severity:
        checklist.append("同步主管或值班负责人，超过 15 分钟未恢复即升级。")
    if hits:
        checklist.append(f"优先参考《{hits[0].chunk.source}》中的「{hits[0].chunk.section}」。")
    checklist.append("处理完成后补充根因、最终方案和复盘建议。")
    return checklist


class OpsAgent:
    def __init__(self, kb: KnowledgeBase, provider: LLMProvider):
        self.kb = kb
        self.provider = provider

    def assist(self, question: str, scenario: str = "general") -> AssistResponse:
        hits = self.kb.search(question, scenario=scenario, top_k=4)
        severity, owner_team, sla = classify_issue(question, scenario)
        context = [
            {
                "source": hit.chunk.source,
                "scenario": hit.chunk.scenario,
                "section": hit.chunk.section,
                "content": hit.chunk.content,
                "score": str(hit.score),
            }
            for hit in hits
        ]
        system_prompt = (
            "你是企业一线运营 Agent。只基于给定知识库和用户问题回答。"
            "输出要具体、可执行、可审计。遇到高风险问题要先止损再排查。"
        )
        raw_answer = self.provider.generate(system_prompt, question, context)
        checklist = make_checklist(question, hits, severity)
        citations = [
            Citation(
                source=hit.chunk.source,
                section=hit.chunk.section,
                score=hit.score,
                content=hit.chunk.content[:500],
            )
            for hit in hits
        ]
        return AssistResponse(
            answer=raw_answer,
            severity=severity,
            owner_team=owner_team,
            suggested_sla=sla,
            checklist=checklist,
            citations=citations,
        )
