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
    """Rank sentences with BM25, rejecting weak lexical matches."""
    query_terms = list(dict.fromkeys(tokenize(question)))
    if not query_terms or limit <= 0:
        return []

    query_set = set(query_terms)
    minimum_matches = _minimum_match_count(len(query_set))
    minimum_coverage = _minimum_coverage(len(query_set))

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
        matched = query_set.intersection(frequencies)
        coverage = len(matched) / len(query_set)

        # A one- or two-concept question must match every concept. Longer
        # questions may omit some wording, but still need multiple anchors.
        if len(matched) < minimum_matches or coverage < minimum_coverage:
            continue

        score = 0.0
        for term in query_terms:
            tf = frequencies[term]
            if not tf:
                continue
            df = document_frequency[term]
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            denominator = tf + k1 * (1 - b + b * len(item.terms) / max(avg_len, 1))
            score += idf * ((tf * (k1 + 1)) / denominator)

        if score <= 0:
            continue

        # Reward broad query coverage modestly; exact short phrases receive
        # a small bonus, but neither can rescue a sentence that failed filtering.
        score *= 0.75 + 0.25 * coverage
        if _contains_phrase(query_terms, item.terms):
            score *= 1.2

        ranked.append(
            Evidence(
                sentence=item.sentence,
                title=item.title,
                url=item.url,
                source=item.source,
                score=score,
                matched_terms=tuple(sorted(matched)),
                query_coverage=coverage,
            )
        )

    ranked.sort(key=lambda evidence: evidence.score, reverse=True)
    return _deduplicate(ranked, limit)


def _minimum_match_count(term_count: int) -> int:
    if term_count <= 2:
        return term_count
    if term_count <= 4:
        return 2
    if term_count <= 8:
        return 3
    return 4


def _minimum_coverage(term_count: int) -> float:
    if term_count <= 2:
        return 1.0
    if term_count <= 4:
        return 0.5
    if term_count <= 8:
        return 0.35
    return 0.25


def _contains_phrase(query_terms: list[str], sentence_terms: list[str]) -> bool:
    if len(query_terms) < 2 or len(query_terms) > 5:
        return False
    width = len(query_terms)
    return any(
        sentence_terms[index:index + width] == query_terms
        for index in range(len(sentence_terms) - width + 1)
    )


def _deduplicate(items: list[Evidence], limit: int) -> list[Evidence]:
    selected: list[Evidence] = []
    seen: list[frozenset[str]] = []
    for item in items:
        signature = frozenset(tokenize(item.sentence))
        if not signature:
            continue
        if any(_jaccard(signature, old) > 0.82 for old in seen):
            continue
        seen.append(signature)
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0
