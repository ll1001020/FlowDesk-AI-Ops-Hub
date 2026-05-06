from pathlib import Path

from app.rag import KnowledgeBase, tokenize


def test_tokenize_chinese_and_english():
    tokens = tokenize("收银机 USB 扫码失败")
    assert "usb" in tokens
    assert "收" in tokens


def test_search_retail_sop():
    kb = KnowledgeBase(Path("data/knowledge"))
    hits = kb.search("收银机无法扫码 顾客排队", scenario="retail_ops")
    assert hits
    assert hits[0].chunk.source == "retail_ops.md"
    assert "扫码" in hits[0].chunk.content
