from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Input, RichLog, Static

from .models import Answer
from .pipeline import answer_question


class NoLLMApp(App[None]):
    """A lightweight chat-style terminal interface for the evidence engine."""

    TITLE = "NoLLM"
    SUB_TITLE = "Local-first evidence engine"

    CSS = """
    Screen {
        background: #0b0e13;
        color: #e6edf3;
    }

    #layout {
        height: 1fr;
        margin: 1 2;
        border: round #34404f;
        background: #0d1117;
    }

    #brand {
        height: 3;
        padding: 0 2;
        content-align: left middle;
        background: #141b24;
        color: #e6edf3;
        text-style: bold;
        border-bottom: solid #34404f;
    }

    #status {
        height: 1;
        padding: 0 2;
        background: #10161e;
        color: #91a4b8;
    }

    #transcript {
        height: 1fr;
        padding: 1 2;
        background: #0d1117;
    }

    #composer {
        height: auto;
        padding: 1 2;
        background: #141b24;
        border-top: solid #34404f;
    }

    #prompt {
        width: 1fr;
        height: 3;
        border: round #4b5a6c;
        background: #0b0e13;
    }

    #hint {
        height: 1;
        padding: 0 2;
        background: #10161e;
        color: #77879a;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+l", "clear_chat", "Clear chat"),
    ]

    def __init__(
        self,
        initial_urls: list[str] | None = None,
        initial_files: list[str] | None = None,
        web_enabled: bool = True,
        wiki_enabled: bool = True,
        wiki_limit: int = 5,
    ) -> None:
        super().__init__()
        self.initial_urls = list(initial_urls or [])
        self.local_files: list[str] = []
        for value in initial_files or []:
            path = Path(value).expanduser()
            if path.is_file():
                self.local_files.append(str(path.resolve()))
        self.web_enabled = web_enabled
        self.wiki_enabled = wiki_enabled
        self.wiki_limit = max(1, wiki_limit)
        self.last_answer: Answer | None = None
        self._busy = False

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("NoLLM  /  LOCAL RESEARCH", id="brand"),
            Static(self._status_text(), id="status"),
            RichLog(
                id="transcript",
                max_lines=800,
                min_width=40,
                wrap=True,
                markup=False,
                highlight=False,
            ),
            Vertical(
                Input(
                    placeholder="Ask a question…  (type /help for commands)",
                    id="prompt",
                ),
                Static(
                    "Enter send · /help · /load <path> · /files · /sources · "
                    "/offline · /online · Ctrl+Q quit",
                    id="hint",
                ),
                id="composer",
            ),
            id="layout",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._log(
            "SYSTEM",
            "Welcome to NoLLM. Answers are assembled from retrieved evidence; "
            "no large language model is used.",
        )
        self._log("SYSTEM", "Type /help to see commands. Ask a factual question to begin.")
        if self.local_files:
            self._log("SYSTEM", f"Loaded {len(self.local_files)} local file(s) into the research context.")
        self.query_one("#prompt", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        event.input.value = ""
        if not prompt:
            return

        if self._busy:
            self._log("SYSTEM", "A research query is already running. Please wait.")
            return

        if prompt.startswith("/"):
            self._handle_command(prompt)
            event.input.focus()
            return

        self._log("YOU", prompt)
        self._busy = True
        event.input.disabled = True
        self.query_one("#status", Static).update("RESEARCHING  ·  RETRIEVING SOURCES  ·  PLEASE WAIT")
        self._research(prompt)

    @work(thread=True, exclusive=True, group="research")
    def _research(self, prompt: str) -> None:
        """Run potentially slow network and retrieval work outside the UI thread."""
        try:
            answer = answer_question(
                prompt,
                urls=self.initial_urls if self.web_enabled else [],
                files=self.local_files,
                wiki_limit=self.wiki_limit,
                use_wikipedia=self.web_enabled and self.wiki_enabled,
            )
        except Exception as exc:
            self.call_from_thread(self._finish_error, str(exc))
            return
        self.call_from_thread(self._finish_answer, answer)

    def _finish_answer(self, answer: Answer) -> None:
        self.last_answer = answer
        self._log("NOLLM", answer.text)
        self._log(
            "EVIDENCE SUFFICIENCY",
            f"{answer.confidence:.0%}  (retrieval sufficiency, not probability of truth)",
        )
        if answer.evidence:
            source_lines = [
                f"[{index}] {item.title}\n    {item.url}"
                for index, item in enumerate(answer.evidence, 1)
            ]
            self._log("SOURCES", "\n".join(source_lines))
        else:
            self._log("SOURCES", "No sufficiently relevant evidence was found.")
        self._finish_request()

    def _finish_error(self, message: str) -> None:
        self._log("ERROR", f"Research failed: {message}")
        self._finish_request()

    def _finish_request(self) -> None:
        self._busy = False
        prompt = self.query_one("#prompt", Input)
        prompt.disabled = False
        self.query_one("#status", Static).update(self._status_text())
        prompt.focus()

    def _handle_command(self, raw: str) -> None:
        command, _, argument = raw.partition(" ")
        command = command.lower()
        argument = argument.strip()

        if command == "/help":
            self._log(
                "HELP",
                "/load <path>  Load a local text/code/Markdown/HTML file (quote paths with spaces).\n"
                "/files        List loaded local files.\n"
                "/sources      Show sources from the previous answer.\n"
                "/offline      Disable all web access; use loaded files only.\n"
                "/online       Re-enable web access.\n"
                "/clear        Clear the visible conversation.\n"
                "/help         Show this help.\n"
                "Ctrl+L        Clear the visible conversation.\n"
                "Ctrl+Q        Quit NoLLM.",
            )
        elif command == "/clear":
            self.query_one("#transcript", RichLog).clear()
            self.last_answer = None
            self._log("SYSTEM", "Conversation view cleared.")
        elif command == "/sources":
            if not self.last_answer or not self.last_answer.evidence:
                self._log("SOURCES", "There are no sources for the previous answer.")
            else:
                lines = [
                    f"[{index}] {item.title}\n    {item.url}\n    {item.sentence}"
                    for index, item in enumerate(self.last_answer.evidence, 1)
                ]
                self._log("SOURCES", "\n".join(lines))
        elif command == "/files":
            if not self.local_files:
                self._log("FILES", "No local files loaded. Use /load <path> to add one.")
            else:
                self._log("FILES", "\n".join(self.local_files))
        elif command == "/load":
            self._load_file(argument)
        elif command == "/offline":
            self.web_enabled = False
            self.query_one("#status", Static).update(self._status_text())
            self._log("SYSTEM", "Web research disabled. Only loaded local files will be searched.")
            if not self.local_files:
                self._log("SYSTEM", "No local files are loaded yet. Use /load <path> to add a document.")
        elif command == "/online":
            self.web_enabled = True
            self.query_one("#status", Static).update(self._status_text())
            self._log("SYSTEM", "Web research enabled.")
        else:
            self._log("SYSTEM", f"Unknown command: {command}. Type /help for available commands.")

    def _load_file(self, argument: str) -> None:
        value = argument.strip().strip('"').strip("'")
        if not value:
            self._log("SYSTEM", 'Usage: /load "C:\\path\\to\\document.txt"')
            return

        path = Path(value).expanduser()
        if not path.is_file():
            self._log("SYSTEM", f"File not found: {path}")
            return

        resolved = str(path.resolve())
        if resolved in self.local_files:
            self._log("SYSTEM", f"Already loaded: {resolved}")
            return

        self.local_files.append(resolved)
        self.query_one("#status", Static).update(self._status_text())
        self._log("SYSTEM", f"Loaded local file: {resolved}")

    def _status_text(self) -> str:
        mode = "ONLINE" if self.web_enabled else "OFFLINE"
        wiki = "WIKIPEDIA ON" if self.web_enabled and self.wiki_enabled else "WIKIPEDIA OFF"
        return (
            f"{mode}  ·  {wiki}  ·  {len(self.local_files)} LOCAL FILE(S)  ·  "
            "NO LLM  ·  CPU-FIRST"
        )

    def _log(self, label: str, message: str) -> None:
        transcript = self.query_one("#transcript", RichLog)
        transcript.write(f"\n{label}\n{'─' * max(4, len(label))}\n{message}\n", scroll_end=True)

    def action_clear_chat(self) -> None:
        self.query_one("#transcript", RichLog).clear()
        self.last_answer = None
        self._log("SYSTEM", "Conversation view cleared.")
