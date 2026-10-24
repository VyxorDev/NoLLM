# NoLLM

A local-first, low-resource AI research engine built **without large language models**.

NoLLM searches available sources, retrieves relevant evidence, ranks it, and composes a deterministic answer. It is designed to run on CPU-only and low-resource computers.

## Current capabilities

- zero required third-party dependencies for the core engine
- zero API keys and no mandatory GPU
- free Wikipedia discovery through MediaWiki
- direct webpage ingestion with `--url`
- local text/HTML ingestion with `--file`
- fully offline one-shot research with `--file --no-wiki`
- HTML-to-text extraction
- BM25 sentence retrieval with weak-match filtering
- duplicate suppression and publisher diversity
- conservative evidence-sufficiency scoring (not a truth probability)
- deterministic answer composition with source citations
- standard-library unit tests
- optional interactive terminal chat UI

## Install

Requires Python 3.10+.

Create an environment and install the core:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

To enable the interactive terminal UI, install the optional extra:

```powershell
python -m pip install -e ".[tui]"
```

The core remains dependency-free; the TUI uses Textual and does not require a GPU or AI model.

## Run

Launch the interactive terminal chat (requires the optional `tui` extra):

```powershell
nollm
```

You can also explicitly launch the TUI:

```powershell
nollm --tui
```

Ask a one-shot question:

```powershell
nollm "What is a knowledge graph?" --show-evidence
```

Include arbitrary webpages:

```powershell
nollm "What changed in this project?" --url https://example.com/page --show-evidence
```

Run a fully offline query against a local file:

```powershell
nollm "What does this document say about BM25?" --file .\notes.txt --no-wiki --show-evidence
```

If the TUI extra is not installed, one-shot commands still work. Running `nollm` without a question prints the exact install command needed to enable chat.

## TUI commands

Inside the interactive terminal chat:

- `/help` — show commands
- `/load <path>` — add a local text, code, Markdown, or HTML file to the research context (quote paths containing spaces)
- `/files` — list loaded local files
- `/sources` — show the evidence sources for the previous answer
- `/offline` — disable web discovery and use loaded local files only
- `/online` — enable web discovery
- `/clear` — clear the visible conversation
- `Ctrl+L` — clear the conversation
- `Ctrl+Q` — quit

The transcript is bounded to 800 lines to keep memory usage predictable. Each answer shows its evidence-sufficiency estimate and source URLs.

## Run without installing the CLI entry point

```powershell
$env:PYTHONPATH = "src"
python -m nolllm "What is BM25?" --show-evidence
```

## Architecture

```text
question
   |
   v
free discovery / supplied URLs / local files
   |
   v
text extraction
   |
   v
sentence segmentation
   |
   v
BM25 retrieval + weak-match filtering
   |
   v
source diversity + evidence sufficiency
   |
   v
deterministic answer composer
```

## Design rules

1. No large language model dependency.
2. GPU is optional, never required.
3. Low-end hardware must remain supported.
4. Prefer deterministic algorithms before neural models.
5. Heavy features must be optional/lazy-loaded.
6. Factual answers should remain traceable to evidence.
7. No paid service may become mandatory.

## Roadmap

### V0.3 — claim verification
- claim extraction and normalization
- agreement/contradiction detection
- dates and numeric facts
- provenance graph
- confidence calibration against test cases

### V0.4 — broader web discovery
- pluggable search-provider interface
- optional SearXNG provider
- documentation-site search adapters
- robots.txt-aware fetching
- cache with disk-size limits

### V0.5 — local memory
- SQLite knowledge store
- entity/relationship graph
- source reliability history
- incremental cache/index

### V0.6 — specialist reasoning
- math via SymPy
- constraints/logic via Z3
- graph algorithms
- rule engine
- task routing

### V0.7 — coding engine
- AST parsing
- template and grammar-based synthesis
- documentation retrieval
- compiler/test execution
- repair loop

## Tests

Core test suite:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The CI workflow also installs the optional TUI extra and runs the UI smoke tests.

## License

MIT
