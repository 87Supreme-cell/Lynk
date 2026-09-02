# Build log

This is the human-readable engineering ledger for Lynk. Git commits remain the
authoritative record of exact code changes; this file explains intent,
validation, constraints, and next steps without including private reasoning or
user data.

## Entry template

```md
## YYYY-MM-DD - Short milestone title

**Goal**

**Implemented**

**Affected modules**

**Decisions**

**Validation**

**Known limitations / next step**

**Commit**
```

## 2026-09-01 - Milestone 1: local document-ingestion foundation

**Goal**

Create a local, provenance-preserving foundation for user document ingestion.

**Implemented**

- Added text, Markdown, and PDF ingestion.
- Added immutable local copies, SHA-256 hashes, page-level extraction, and a
  pluggable local OCR fallback.
- Added a SQLite document/page catalog and local `lynk ingest` / `lynk documents`
  CLI commands.
- Added project policy, architecture documentation, and synthetic tests.

**Affected modules**

- `src/lynk/ingestion.py`
- `src/lynk/catalog.py`
- `src/lynk/cli.py`
- `src/lynk/models.py`
- `tests/`
- `docs/architecture.md`

**Decisions**

- Decided to add a committed engineering ledger so the path from an empty
  repository to a working, evidence-governed research agent is visible during
  interviews.
- Decided to require the coding agent to update this ledger for meaningful code
  changes, preserving the goal, validation, limitations, and next step without
  recording private reasoning, credentials, or user documents.

**Validation**

- `pytest`: 4 tests passed.
- `ruff check .`: passed.
- CLI smoke test: ingested and listed a local text document.

**Known limitations / next step**

- Image-only PDFs require local OCRmyPDF when OCR is enabled.
- The project does not yet chunk documents, create embeddings, retrieve RAG
  context, or call a language model.
- Next: page-aware chunking, local embeddings, and filtered retrieval.

**Commit**

- `51f957b` - `feat: add local document ingestion foundation`
