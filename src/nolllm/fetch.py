from __future__ import annotations

import json
from pathlib import Path
import urllib.parse
import urllib.request

from .models import Document
from .text import html_to_text

USER_AGENT = "NoLLM-AI/0.1 (+https://github.com/)"


def fetch_url(url: str, timeout: float = 12.0, max_bytes: int = 2_000_000) -> Document:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get_content_type()
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError(f"Page exceeds {max_bytes:,} byte safety limit")
        if content_type not in {"text/html", "text/plain", "application/xhtml+xml"}:
            raise ValueError(f"Unsupported content type: {content_type}")
        body = raw.decode(charset, errors="replace")

    text = html_to_text(body) if "html" in content_type else body
    return Document(title=url, url=url, text=text, source="url")


def wikipedia_search(query: str, limit: int = 5, timeout: float = 12.0) -> list[Document]:
    """Keyless search using the public MediaWiki API."""
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": str(limit),
            "prop": "extracts|info",
            "explaintext": "1",
            "exintro": "0",
            "inprop": "url",
            "format": "json",
            "formatversion": "2",
        }
    )
    url = f"https://en.wikipedia.org/w/api.php?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)

    pages = payload.get("query", {}).get("pages", [])
    documents: list[Document] = []
    for page in pages:
        extract = (page.get("extract") or "").strip()
        if not extract:
            continue
        documents.append(
            Document(
                title=page.get("title", "Wikipedia"),
                url=page.get("fullurl", "https://en.wikipedia.org/"),
                text=extract,
                source="wikipedia",
            )
        )
    return documents


def load_file(path: str) -> Document:
    file_path = Path(path)
    raw = file_path.read_text(encoding="utf-8", errors="replace")
    text = html_to_text(raw) if file_path.suffix.lower() in {".html", ".htm"} else raw
    return Document(title=file_path.name, url=file_path.resolve().as_uri(), text=text, source="file")
