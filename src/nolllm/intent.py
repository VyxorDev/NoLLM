from __future__ import annotations

import re


def _normalize(message: str) -> str:
    """Normalize simple chat input without interpreting its meaning."""
    value = message.casefold().strip()
    value = re.sub(r"[^\w\s']", " ", value)
    return re.sub(r"\s+", " ", value).strip(" '")

_GREETING = {
    "hi", "hello", "hey", "hey there", "hello there", "hi there",
    "yo", "sup", "howdy", "what's up", "whats up",
    "good morning", "good afternoon", "good evening",
    "hi bro", "hello bro", "hey bro",
}

_WELLBEING = {
    "how are you", "how are you doing", "how's it going", "hows it going",
}

_THANKS = {
    "thanks", "thank you", "thanks a lot", "thank you so much",
    "thx", "ty", "appreciate it", "thanks bro", "thank you bro",
}

_GOODBYE = {
    "bye", "goodbye", "see you", "see you later", "good night", "cya",
}

_RESPONSES = {
    "greeting": (
        "Hey! 👋 I'm NoLLM. I can research questions using sources or work "
        "with local files. What would you like to look into?"
    ),
    "wellbeing": (
        "I'm running fine—thanks for asking! I'm a local-first research tool, "
        "so ask me a question whenever you're ready."
    ),
    "thanks": "You're welcome! Ask me whenever you need to research something.",
    "goodbye": "See you later! NoLLM will be here when you need it.",
    "identity": (
        "I'm NoLLM, a local-first research engine. I retrieve and rank evidence "
        "from web pages or local files, then compose deterministic answers "
        "without using a large language model."
    ),
    "capabilities": (
        "I can research factual questions from available web sources, inspect "
        "local text/code/Markdown/HTML files, and show the evidence behind answers. "
        "I don't generate unrestricted text like an LLM. Type /help for commands "
        "or /load <path> to add a local file."
    ),
    "help": (
        "Ask a factual question to research it. Use /help for commands, "
        "/load <path> to add a local file, /files to list loaded files, "
        "/sources to revisit evidence, and /offline to disable web access."
    ),
}


def respond_to_conversation(message: str) -> str | None:
    """Respond to a small set of exact conversational intents without retrieval.

    Returns None for anything that may be a real question or research request.
    This deliberately uses exact normalized phrases rather than fuzzy matching,
    so a question such as 'What does the word hi mean?' still reaches research.
    """
    normalized = _normalize(message)

    if normalized in _GREETING:
        return _RESPONSES["greeting"]
    if normalized in _WELLBEING:
        return _RESPONSES["wellbeing"]
    if normalized in _THANKS:
        return _RESPONSES["thanks"]
    if normalized in _GOODBYE:
        return _RESPONSES["goodbye"]
    if normalized in {"who are you", "what are you", "are you an ai"}:
        return _RESPONSES["identity"]
    if normalized in {"what can you do", "what can nollm do", "your capabilities"}:
        return _RESPONSES["capabilities"]
    if normalized in {"help", "what commands are available"}:
        return _RESPONSES["help"]

    return None
