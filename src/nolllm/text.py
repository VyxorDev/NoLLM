from __future__ import annotations

import html
import re
from html.parser import HTMLParser

_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_+.#'-]*")
_SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

# Small stopword list on purpose: low-memory and deterministic.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "which", "who", "why", "with", "you",
}


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD.findall(text) if w.lower() not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    parts = _SENTENCE.split(cleaned)
    return [p.strip() for p in parts if 25 <= len(p.strip()) <= 700]


class _VisibleTextParser(HTMLParser):
    BLOCKED = {"script", "style", "noscript", "svg", "canvas", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.lower() in self.BLOCKED:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.BLOCKED and self.depth:
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.depth == 0:
            value = data.strip()
            if value:
                self.parts.append(value)


def html_to_text(raw_html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(raw_html)
    return html.unescape(re.sub(r"\s+", " ", " ".join(parser.parts))).strip()
