# NoLLM AI

A local-first, low-resource AI research engine built **without large language models**.

The long-term goal is to push retrieval, symbolic reasoning, program synthesis, verification, planning, and classical NLP as far as possible while keeping GPU use optional and hardware requirements low.

## V0.1: first working core

This first version already has:

- zero required third-party Python dependencies
- zero API keys
- zero GPU requirement
- free Wikipedia discovery through MediaWiki
- direct webpage ingestion with `--url`
- fully offline local text/HTML ingestion with `--file --no-wiki`
- HTML-to-text extraction
- a small BM25 sentence retriever implemented from scratch
- duplicate suppression
- lightweight evidence rescoring
- deterministic answer composition
- source/evidence display
- standard-library unit tests

It is intentionally small. We should earn complexity only when a cheaper algorithm cannot do the job.

## Install

Requires Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Run

```powershell
nolllm "What is a knowledge graph?" --show-evidence
```

Include arbitrary webpages:

```powershell
nolllm "What changed in this project?" --url https://example.com/page --show-evidence
```

Fully offline:

```powershell
nolllm "What does this document say about BM25?" --file .\notes.txt --no-wiki --show-evidence
```

Or without installing the CLI entry point:

```powershell
$env:PYTHONPATH="src"
python -m nolllm "What is BM25?" --show-evidence
```

## Architecture

```text
question
   |
   v
free discovery / supplied URLs
   |
   v
text extraction
   |
   v
sentence segmentation
   |
   v
BM25 retrieval
   |
   v
evidence rescoring + deduplication
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
6. Every factual answer should remain traceable to evidence.
7. No paid service may become mandatory.

## Roadmap

### V0.2 — real web discovery
- pluggable search-provider interface
- SearXNG provider
- documentation-site search adapters
- robots.txt-aware fetching
- cache with disk-size limits

### V0.3 — stronger evidence engine
- claim extraction
- agreement/contradiction detection
- dates and numeric facts
- source independence detection
- provenance graph
- confidence calibration

### V0.4 — local memory
- SQLite knowledge store
- entity/relationship graph
- source reliability history
- incremental cache/index

### V0.5 — specialist reasoning
- math via SymPy
- constraints/logic via Z3
- graph algorithms
- rule engine
- task routing

### V0.6 — coding engine
- Tree-sitter/AST parsing
- template and grammar-based synthesis
- documentation retrieval
- compiler/test execution
- repair loop

### Later
- lightweight dialogue manager
- planning/search algorithms
- combinatorial creativity engine
- optional tiny classifiers/embedders where they clearly beat classical methods
- automatic hardware profile: tiny / normal / max

## Tests

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## License

MIT
