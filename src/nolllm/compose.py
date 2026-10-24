from __future__ import annotations

from .models import Answer, Evidence


def compose(question: str, evidence: list[Evidence], max_points: int = 4) -> Answer:
    if not evidence:
        return Answer(
            question=question,
            text="I could not find enough relevant evidence to answer this reliably.",
            evidence=[],
            confidence=0.0,
        )

    chosen = _diverse_sources(evidence, max_points)
    top = evidence[0].score
    source_count = len({item.url for item in chosen})
    coverage = min(1.0, len(chosen) / max_points)
    confidence = min(0.95, 0.25 + 0.25 * coverage + 0.12 * min(source_count, 3) + 0.08 * min(top, 2.0))

    if len(chosen) == 1:
        body = chosen[0].sentence
    else:
        body = " ".join(item.sentence for item in chosen)

    prefix = "The strongest retrieved evidence indicates: "
    return Answer(question=question, text=prefix + body, evidence=chosen, confidence=confidence)


def _diverse_sources(evidence: list[Evidence], limit: int) -> list[Evidence]:
    chosen: list[Evidence] = []
    source_use: dict[str, int] = {}
    for item in evidence:
        if source_use.get(item.url, 0) >= 2:
            continue
        chosen.append(item)
        source_use[item.url] = source_use.get(item.url, 0) + 1
        if len(chosen) >= limit:
            break
    return chosen
