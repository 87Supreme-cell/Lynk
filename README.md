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

This is not yet a complete RAG agent. The repository now includes the
versioned PostgreSQL/pgvector retrieval schema; embeddings, retrieval, web
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

## Local PostgreSQL and pgvector

The long-term RAG store is local PostgreSQL with pgvector. Start the local
database, then use the PostgreSQL catalog explicitly:

```bash
cp .env.example .env
docker compose --env-file .env up -d postgres
export LYNK_DATABASE_URL='postgresql://lynk:change-me-for-local-development@localhost:5433/lynk'
lynk ingest /path/to/document.pdf --data-dir ./data --storage postgres
lynk documents --storage postgres
```

The schema uses relational columns for frequent filters, JSONB for evolving
metadata, pgvector for future semantic embeddings, and full-text indexes for
keyword retrieval. The agent will access these only through safe, parameterized
retrieval tools described by a schema registry; it will not generate arbitrary
SQL.

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

See [docs/architecture.md](docs/architecture.md),
[docs/build-log.md](docs/build-log.md), [docs/decisions](docs/decisions), and
[AGENTS.md](AGENTS.md).
