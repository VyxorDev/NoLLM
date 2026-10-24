from __future__ import annotations

from .compose import compose
from .evidence import rescore
from .fetch import fetch_url, load_file, wikipedia_search
from .models import Answer, Document
from .retrieval import retrieve


def answer_question(
    question: str,
    urls: list[str] | None = None,
    files: list[str] | None = None,
    wiki_limit: int = 5,
    use_wikipedia: bool = True,
) -> Answer:
    documents: list[Document] = []

    if use_wikipedia:
        # Free, keyless baseline discovery. More providers can plug in later.
        documents.extend(wikipedia_search(question, limit=wiki_limit))

    for url in urls or []:
        try:
            documents.append(fetch_url(url))
        except Exception:
            # One broken page must not kill the whole research run.
            continue

    for path in files or []:
        try:
            documents.append(load_file(path))
        except Exception:
            continue

    evidence = retrieve(question, documents, limit=12)
    evidence = rescore(evidence)
    return compose(question, evidence)
