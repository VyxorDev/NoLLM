from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Document:
    title: str
    url: str
    text: str
    source: str = "web"


@dataclass(slots=True)
class Evidence:
    sentence: str
    title: str
    url: str
    score: float
    source: str = "web"
    matched_terms: tuple[str, ...] = field(default_factory=tuple)
    query_coverage: float = 0.0


@dataclass(slots=True)
class Answer:
    question: str
    text: str
    evidence: list[Evidence]
    confidence: float
