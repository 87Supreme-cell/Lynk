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

## 2026-09-01 - Decision: local-first repository recovery

**Goal**

Make the build reproducible and auditable even when a GitHub push fails or a
remote branch needs recovery.

**Decisions**

- The local Git working tree and committed history are the immediate source of
  recovery; GitHub is a synchronized remote replica, not the only copy of the
  build.
- All meaningful work is made on a named branch and committed locally before a
  remote push. A failed push leaves the local commit history intact and ready
  to retry, inspect, or move to another remote.
- Do not use force pushes or destructive Git resets for normal work. Preserve
  the audit trail through additive commits and documented decisions.
- Keep private `data/`, document originals, local databases, secrets, and
  model weights out of Git. Their backup and restore process is a separate
  future decision; this repository recovery policy protects reproducible code,
  configuration, tests, and documentation.

**Validation**

- The project is developed on a dedicated `codex/` branch with local commits
  pushed only after validation.
- `docs/build-log.md`, `docs/decisions/`, and Git commits provide linked,
  human-readable and machine-verifiable audit history.

**Known limitations / next step**

- Add a documented, encrypted local backup routine for private `data/` once
  user documents and databases are introduced.

**Commit**

- Pending this decision-record commit.

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
