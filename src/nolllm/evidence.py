from __future__ import annotations

from collections import Counter

from .models import Evidence

SOURCE_WEIGHT = {
    "url": 1.0,
    "file": 1.0,
    "wikipedia": 0.9,
    "web": 0.85,
}


def rescore(evidence: list[Evidence]) -> list[Evidence]:
    """Apply cheap source diversity and corroboration bonuses."""
    if not evidence:
        return []

    term_sources: dict[str, set[str]] = {}
    for item in evidence:
        for term in item.matched_terms:
            term_sources.setdefault(term, set()).add(item.url)

    rescored: list[Evidence] = []
    source_counts = Counter(item.url for item in evidence)
    for item in evidence:
        corroboration = sum(max(0, len(term_sources[t]) - 1) for t in item.matched_terms)
        diversity_penalty = 1 / (1 + 0.08 * max(0, source_counts[item.url] - 1))
        item.score *= SOURCE_WEIGHT.get(item.source, 0.8)
        item.score *= 1 + min(corroboration, 6) * 0.025
        item.score *= diversity_penalty
        rescored.append(item)

    return sorted(rescored, key=lambda e: e.score, reverse=True)
