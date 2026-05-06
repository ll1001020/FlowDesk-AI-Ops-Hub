from pathlib import Path

from app.agent import OpsAgent, classify_issue
from app.providers.mock import MockProvider
from app.rag import KnowledgeBase


def test_classify_high_priority():
    severity, owner, sla = classify_issue("设备高温并且有安全风险，可能停机", "device_inspection")
    assert severity.startswith("P1")
    assert "设备" in owner
    assert "15" in sla


def test_agent_assist_contains_citations():
    kb = KnowledgeBase(Path("data/knowledge"))
    agent = OpsAgent(kb, MockProvider())
    result = agent.assist("教学楼空调漏水，现场应该先做什么？", "campus_ops")
    assert result.citations
    assert result.severity in {"P1 高优先级", "P2 中优先级", "P3 常规优先级"}
    assert result.checklist
