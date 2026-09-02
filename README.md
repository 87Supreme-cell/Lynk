# Lynk

Lynk is a local, evidence-governed research agent. It is designed to ingest
personal documents and approved public sources, preserve provenance, identify
research gaps, and produce reviewable, cited briefings before information is
promoted to long-term RAG.

## Milestone 1: local document ingestion

This release creates the foundation for trustworthy retrieval:

- copies original files into local storage without modifying the source;
- hashes every document for duplicate detection and provenance;
- extracts text page by page from text, Markdown, and PDF files;
- flags image-only PDF pages for a pluggable OCR fallback;
- persists document metadata and extracted pages in local SQLite;
- exposes a local CLI and has deterministic tests.

This is not yet a complete RAG agent. Vector embeddings, retrieval, web
research, review/promotion, and a local model adapter follow in later
milestones.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
lynk ingest /path/to/document.pdf --data-dir ./data
lynk documents --data-dir ./data
pytest
```

By default, `data/` is intentionally ignored by Git. Keep private documents,
database files, model weights, and secrets local. Commit only synthetic or
public fixtures and reproducible scripts.

## Architecture

```text
user document
  -> immutable local copy + SHA-256
  -> text/PDF extractor -> OCR fallback when needed
  -> page-level provenance + SQLite catalog
  -> [next] chunking, embeddings, hybrid retrieval, review-gated RAG
```

See [docs/architecture.md](docs/architecture.md) and [AGENTS.md](AGENTS.md).

