from __future__ import annotations

import argparse
import sys

from .pipeline import answer_question


TUI_INSTALL_HINT = 'The interactive TUI is optional. Install it with: python -m pip install -e ".[tui]"'


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nollm",
        description="Low-resource evidence engine with no large language model.",
    )
    parser.add_argument(
        "question",
        nargs="*",
        help="Question to research; omit it to open the interactive terminal chat",
    )
    parser.add_argument("--tui", action="store_true", help="Open the interactive terminal chat")
    parser.add_argument("--url", action="append", default=[], help="Extra webpage to include (repeatable)")
    parser.add_argument("--file", action="append", default=[], help="Local text/HTML file to include (repeatable)")
    parser.add_argument("--wiki-limit", type=int, default=5, help="Wikipedia pages to retrieve")
    parser.add_argument("--no-wiki", action="store_true", help="Disable Wikipedia discovery")
    parser.add_argument("--show-evidence", action="store_true", help="Show ranked evidence and source URLs")
    return parser


def _launch_tui(args: argparse.Namespace) -> int:
    try:
        from .tui import NoLLMApp
    except ModuleNotFoundError as exc:
        if exc.name == "textual" or (exc.name or "").startswith("textual."):
            print(TUI_INSTALL_HINT, file=sys.stderr)
            return 2
        raise

    NoLLMApp(
        initial_urls=args.url,
        initial_files=args.file,
        web_enabled=not args.no_wiki,
    ).run()
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.tui and args.question:
        parser.error("Do not combine --tui with a one-shot question; omit the question to open chat.")

    if args.tui or not args.question:
        return _launch_tui(args)

    question = " ".join(args.question).strip()
    try:
        answer = answer_question(
            question,
            urls=args.url,
            files=args.file,
            wiki_limit=max(1, args.wiki_limit),
            use_wikipedia=not args.no_wiki,
        )
    except Exception as exc:
        print(f"Research failed: {exc}", file=sys.stderr)
        return 1

    print(answer.text)
    print(f"\nEvidence sufficiency (not truth probability): {answer.confidence:.0%}")

    if args.show_evidence and answer.evidence:
        print("\nEvidence:")
        for index, item in enumerate(answer.evidence, 1):
            print(f"[{index}] {item.sentence}")
            print(f"    {item.title} — {item.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
