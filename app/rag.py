import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")


@dataclass
class DocumentChunk:
    source: str
    scenario: str
    section: str
    content: str


@dataclass
class SearchHit:
    chunk: DocumentChunk
    score: float


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def split_markdown(source: Path, text: str) -> Iterable[DocumentChunk]:
    scenario = source.stem
    current_section = "overview"
    buf: List[str] = []

    def flush():
        if buf:
            content = "\n".join(buf).strip()
            if content:
                yield DocumentChunk(source=source.name, scenario=scenario, section=current_section, content=content)

    for line in text.splitlines():
        if line.startswith("#"):
            yield from flush()
            buf = []
            current_section = line.strip("# ") or "section"
        else:
            buf.append(line)
    yield from flush()


class KnowledgeBase:
    def __init__(self, knowledge_dir: Path):
        self.knowledge_dir = knowledge_dir
        self.chunks: List[DocumentChunk] = []
        self.df: defaultdict[str, int] = defaultdict(int)
        self.doc_vectors: List[dict[str, float]] = []
        self.idf: dict[str, float] = {}
        self.load()

    def load(self) -> None:
        self.chunks.clear()
        for path in sorted(self.knowledge_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            self.chunks.extend(split_markdown(path, text))
        self._build_index()

    def _build_index(self) -> None:
        tokenized = [tokenize(chunk.content + " " + chunk.section + " " + chunk.scenario) for chunk in self.chunks]
        for tokens in tokenized:
            for token in set(tokens):
                self.df[token] += 1
        n = max(len(self.chunks), 1)
        self.idf = {t: math.log((1 + n) / (1 + df)) + 1 for t, df in self.df.items()}
        self.doc_vectors = [self._tfidf(tokens) for tokens in tokenized]

    def _tfidf(self, tokens: List[str]) -> dict[str, float]:
        counts = Counter(tokens)
        total = max(sum(counts.values()), 1)
        return {t: (c / total) * self.idf.get(t, 0.0) for t, c in counts.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        common = set(a) & set(b)
        dot = sum(a[t] * b[t] for t in common)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query: str, scenario: str = "general", top_k: int = 4) -> List[SearchHit]:
        expanded_query = query + " " + (scenario or "")
        q_vec = self._tfidf(tokenize(expanded_query))
        hits: List[SearchHit] = []
        for chunk, d_vec in zip(self.chunks, self.doc_vectors):
            score = self._cosine(q_vec, d_vec)
            if scenario and scenario != "general" and chunk.scenario == scenario:
                score *= 1.25
            if score > 0:
                hits.append(SearchHit(chunk=chunk, score=round(score, 4)))
        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:top_k]
