# ADR 0003: Offline resilience and language baseline

**Status:** proposed

## Context

Lynk is intended to be a local research system, but its initial setup and web
research features depend on network access. The project also needs a deliberate
language strategy that is practical for development and defensible in
interviews.

## Decision

After one-time installation and caching, the core local path must work without
network access: local document ingestion, local database retrieval, and local
model inference. The project will add an offline-readiness verification before
claiming this behavior.

Python is the primary application language. SQL is the first-class retrieval
and data-model language. TypeScript is reserved for a future custom frontend or
web API client; Go or Rust require a demonstrated performance, packaging, or
concurrency need.

## Alternatives considered

### Treat a network connection as required for every feature

Rejected because it undermines the local-first privacy and reliability goal.

### Use multiple languages from the beginning

Rejected because it increases complexity without improving the document,
retrieval, and model-integration work that defines this project.

## Consequences

- Dependencies, Docker images, model weights, and database backups need an
  explicit local cache and restore plan.
- Web research becomes a clearly separate online capability rather than a
  hidden dependency of local RAG.
- The repository remains primarily Python plus SQL, which keeps development and
  review focused.
