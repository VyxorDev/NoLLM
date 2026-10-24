from __future__ import annotations

from .evidence import source_identity
from .models import Answer, Evidence


_NO_EVIDENCE = "I could not find enough relevant evidence to answer this reliably."


def compose(question: str, evidence: list[Evidence], max_points: int = 4) -> Answer:
    if not evidence or max_points <= 0:
        return Answer(question=question, text=_NO_EVIDENCE, evidence=[], confidence=0.0)

    chosen = _diverse_sources(evidence, max_points)
    if not chosen:
        return Answer(question=question, text=_NO_EVIDENCE, evidence=[], confidence=0.0)

    top = chosen[0]
    coverage = max(0.0, min(1.0, top.query_coverage))
    relevance = top.score / (top.score + 2.5) if top.score > 0 else 0.0
    independent_publishers = len({source_identity(item) for item in chosen})
    source_diversity = min(1.0, independent_publishers / 3)
    # This is a conservative retrieval/evidence sufficiency estimate, not a
    # probability that the claim is true. Cap it until claim verification exists.
    confidence = min(0.75, 0.50 * coverage + 0.25 * relevance + 0.10 * source_diversity)

    body = " ".join(item.sentence for item in chosen)
    prefix = "The retrieved evidence suggests: "
    return Answer(question=question, text=prefix + body, evidence=chosen, confidence=confidence)


def _diverse_sources(evidence: list[Evidence], limit: int) -> list[Evidence]:
    """Prefer one item per publisher before taking a second item from any publisher."""
    chosen: list[Evidence] = []
    selected_ids: set[int] = set()
    source_use: dict[str, int] = {}

    for item in evidence:
        identity = source_identity(item)
        if identity in source_use:
            continue
        chosen.append(item)
        selected_ids.add(id(item))
        source_use[identity] = 1
        if len(chosen) >= limit:
            return chosen

    for item in evidence:
        if len(chosen) >= limit:
            break
        if id(item) in selected_ids:
            continue
        identity = source_identity(item)
        if source_use.get(identity, 0) >= 2:
            continue
        chosen.append(item)
        selected_ids.add(id(item))
        source_use[identity] = source_use.get(identity, 0) + 1

    return chosen
