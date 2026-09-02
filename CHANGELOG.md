# Changelog

All notable user-facing changes are documented here. Internal implementation
notes belong in `docs/build-log.md`.

## [Unreleased]

### Added

- Local document ingestion for text, Markdown, and PDFs.
- Local SQLite metadata catalog and provenance-preserving raw storage.
- Page-aware PDF extraction with an optional local OCR fallback.
- Local PostgreSQL/pgvector service definition and versioned SQL retrieval
  schema with relational, JSONB, full-text, and vector-ready records.
