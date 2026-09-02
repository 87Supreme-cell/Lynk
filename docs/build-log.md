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

## 2026-09-02 - Decision: SQL verification before agent drafting

**Goal**

Make retrieval correctness independently observable before relying on a local
model to synthesize or explain evidence.

**Decisions**

- Decided that chunk creation, metadata filters, permission scope, and SQL
  retrieval must be designed and tested as deterministic code before the agent
  is allowed to draft an answer from their output.
- The initial local-model smoke test returned no evidence because the first
  full-text query required every normalized question term to match. The issue
  was diagnosed directly in PostgreSQL and corrected before Qwen was used for a
  successful cited draft.
- Future retrieval work will begin with a documented SQL query, a synthetic
  fixture, expected rows and citations, and an integration test. The model is a
  consumer of verified evidence, not a substitute for retrieval correctness.

**Known limitations / next step**

- Add database integration tests that initialize PostgreSQL, ingest a fixture,
  assert chunk rows and authorized retrieval results, then separately test the
  model-facing draft.

**Commit**

- Pending this decision-record commit.

## 2026-09-02 - Milestone 4 foundation: local retrieval-to-model drafting

**Goal**

Connect the working local model adapter to page-cited, policy-bounded retrieval
so Lynk can draft answers grounded in user-authorized evidence.

**Implemented**

- Added deterministic, page-aware chunking during PostgreSQL ingestion.
- Added restricted PostgreSQL full-text retrieval that validates the resource
  and filters before executing parameterized SQL.
- Added a local research planner and `lynk research` command that passes only
  retrieved evidence to Qwen/Gemma and requires `[S#]` citations in the draft.

**Decisions**

- Kept this first path keyword-based while no separate embedding model is
  configured. Vector retrieval is the next additive layer, not a reason to
  bypass provenance or permission filters.
- The planner returns a draft only; it cannot automatically perform web
  research or promote evidence into curated RAG.

**Known limitations / next step**

- Requires the local PostgreSQL/pgvector service to be running and populated
  through `lynk ingest --storage postgres`.
- Add a local embedding adapter and hybrid keyword/vector reranking next.

**Commit**

- Pending this implementation commit.

## 2026-09-01 - Milestone 3 foundation: local model adapters

**Goal**

Allow Lynk to use an already-installed local Gemma or Qwen model while keeping
the provider, endpoint, model ID, and sampling settings explicit.

**Implemented**

- Added typed adapters for local Ollama and Open WebUI chat-completions
  endpoints.
- Added `lynk models` for discovery and `lynk chat` for a direct local runtime
  smoke test.
- Added model configuration through ignored environment values, with no cloud
  fallback or automatic model download.

**Known limitations / next step**

- At implementation time, Ollama exposed no installed models and Open WebUI was
  not running on its standard local port, so the exact existing Gemma/Qwen IDs
  could not be detected. Start the relevant runtime and run `lynk models` to
  capture the available IDs.
- Next: connect the model adapter to the retrieval planner after chunking and
  hybrid search are implemented.

**Commit**

- Pending this implementation commit.

## 2026-09-01 - Decision proposal: offline resilience and language baseline

**Goal**

Ensure that Lynk can remain usable when the network is unreliable and choose a
small, appropriate language stack for the project.

**Decisions**

- Established offline resilience as a required design goal. After an initial
  installation, local document ingestion, PostgreSQL/pgvector retrieval, and a
  locally hosted model must work without an internet connection.
- Web discovery and first-time downloads of Python packages, Docker images,
  OCR components, model weights, and updates necessarily require connectivity.
  Those dependencies must be explicitly cached, versioned, and tested before
  claiming offline readiness.
- Proposed Python as the primary implementation language because it is the
  strongest fit for document extraction, OCR integration, embeddings, model
  adapters, evaluation, and agent orchestration. SQL is the first-class
  language for the PostgreSQL retrieval schema and queries.
- Defer TypeScript to a future custom web interface and defer Go/Rust to a
  measured performance or deployment need. Avoid adding languages merely for
  portfolio breadth.

**Known limitations / next step**

- Add an offline-readiness runbook and verification test: stop network access
  after local dependencies, Docker images, database volume, and model files are
  present; then prove ingestion, retrieval, and local inference still work.
- Docker Desktop was not running during the PostgreSQL milestone, so live local
  database verification remains pending.

**Commit**

- Pending this decision-record commit.

## 2026-09-01 - Milestone 2 foundation: SQL-first retrieval store

**Goal**

Create a local PostgreSQL/pgvector foundation for metadata-aware RAG while
keeping the initial SQLite catalog as an explicit migration source.

**Implemented**

- Added a Docker Compose PostgreSQL/pgvector service and local environment
  template.
- Added a versioned SQL schema for collections, documents, pages, chunks,
  research runs, retrieval events, review items, and a schema registry.
- Added a PostgreSQL document catalog adapter, a `--storage postgres` CLI
  option, and a restricted retrieval-schema registry for future model planning.

**Decisions**

- Chose PostgreSQL with pgvector as the long-term RAG source of truth because
  its relational model, JSONB metadata, transactional audit trail, full-text
  search, and vector support fit the expected local project scale.
- Kept the model away from arbitrary SQL; it will choose only registered
  retrieval resources and validated filters.

**Validation**

- `pytest`: 6 tests passed.
- `ruff check .`: passed.
- `docker compose config --quiet`: passed.

**Known limitations / next step**

- The Docker daemon was unavailable in this environment, so the live
  PostgreSQL ingestion smoke test remains to be run after Docker Desktop is
  started.
- Next: SQLite-to-PostgreSQL migration utility, page-aware chunks, embeddings,
  and hybrid retrieval queries.

**Commit**

- Pending this implementation commit.

## 2026-09-01 - Decision: SQL-first retrieval on PostgreSQL with pgvector

**Goal**

Define a durable retrieval store that can grow from local document ingestion to
metadata-aware, evidence-governed RAG.

**Decisions**

- Decided to use local PostgreSQL with pgvector as Lynk's long-term retrieval
  store rather than treating a separate vector database as the system of record.
- Store frequently filtered fields in relational columns and evolving document
  metadata, retrieval plans, and decision traces in JSONB. Keep embeddings in
  pgvector and use PostgreSQL full-text search for hybrid retrieval.
- Chose this after considering projected project growth: PostgreSQL provides
  more than sufficient local growth headroom while retaining SQL joins,
  transactions, migrations, auditability, and a portfolio-relevant schema.
- The agent will use a restricted schema registry and parameterized retrieval
  tools, not arbitrary model-generated SQL.

**Known limitations / next step**

- Introduce the local Docker PostgreSQL/pgvector service, versioned schema,
  catalog adapter, and migration path from the initial SQLite catalog.

**Commit**

- Pending this decision-record commit.

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
