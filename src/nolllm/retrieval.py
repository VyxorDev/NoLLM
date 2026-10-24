from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .models import Document, Evidence
from .text import split_sentences, tokenize


@dataclass(slots=True)
class _SentenceDoc:
    sentence: str
    title: str
    url: str
    source: str
    terms: list[str]


def retrieve(question: str, documents: list[Document], limit: int = 8) -> list[Evidence]:
    """Rank sentences with a compact BM25 implementation."""
    query_terms = tokenize(question)
    if not query_terms:
        return []

    corpus: list[_SentenceDoc] = []
    for document in documents:
        for sentence in split_sentences(document.text):
            terms = tokenize(sentence)
            if terms:
                corpus.append(_SentenceDoc(sentence, document.title, document.url, document.source, terms))

    if not corpus:
        return []

    n = len(corpus)
    avg_len = sum(len(item.terms) for item in corpus) / n
    document_frequency: Counter[str] = Counter()
    for item in corpus:
        for term in set(item.terms):
            document_frequency[term] += 1

    k1, b = 1.5, 0.75
    ranked: list[Evidence] = []

    for item in corpus:
        frequencies = Counter(item.terms)
        score = 0.0
        matched: list[str] = []
        for term in query_terms:
            tf = frequencies[term]
            if not tf:
                continue
            matched.append(term)
            df = document_frequency[term]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            denominator = tf + k1 * (1 - b + b * len(item.terms) / max(avg_len, 1))
            score += idf * ((tf * (k1 + 1)) / denominator)

        if score > 0:
            # Prefer sentences that cover several distinct query concepts.
            coverage = len(set(matched)) / max(len(set(query_terms)), 1)
            score *= 1.0 + 0.35 * coverage
            ranked.append(
                Evidence(
                    sentence=item.sentence,
                    title=item.title,
                    url=item.url,
                    source=item.source,
                    score=score,
                    matched_terms=tuple(sorted(set(matched))),
                )
            )

    ranked.sort(key=lambda e: e.score, reverse=True)
    return _deduplicate(ranked, limit)


def _deduplicate(items: list[Evidence], limit: int) -> list[Evidence]:
    selected: list[Evidence] = []
    seen: set[frozenset[str]] = set()
    for item in items:
        signature = frozenset(tokenize(item.sentence))
        if not signature:
            continue
        if any(_jaccard(signature, old) > 0.82 for old in seen):
            continue
        seen.add(signature)
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0
