from __future__ import annotations

from collections import Counter
from dataclasses import replace
from urllib.parse import urlsplit

from .models import Evidence

SOURCE_WEIGHT = {
    "url": 1.0,
    "file": 1.0,
    "wikipedia": 0.9,
    "web": 0.85,
}


def source_identity(item: Evidence) -> str:
    """Return a conservative publisher identity for source-diversity checks."""
    parsed = urlsplit(item.url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if host:
        return host
    # Local paths and non-HTTP sources should remain distinct by location.
    normalized_url = item.url.strip().replace(chr(92), "/").casefold()
    return f"{item.source}:{normalized_url}"


def rescore(evidence: list[Evidence]) -> list[Evidence]:
    """Apply source weighting and reduce the influence of one prolific source.

    Repeated matching terms are not treated as corroboration: true corroboration
    requires claim-level agreement, which this version does not yet establish.
    """
    if not evidence:
        return []

    source_counts = Counter(source_identity(item) for item in evidence)
    rescored: list[Evidence] = []

    for item in evidence:
        identity = source_identity(item)
        source_penalty = 1 / (1 + 0.12 * max(0, source_counts[identity] - 1))
        weight = SOURCE_WEIGHT.get(item.source, 0.8)
        rescored.append(replace(item, score=item.score * weight * source_penalty))

    return sorted(rescored, key=lambda item: item.score, reverse=True)
