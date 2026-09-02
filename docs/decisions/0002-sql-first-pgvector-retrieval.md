# ADR 0002: SQL-first retrieval on PostgreSQL with pgvector

**Status:** accepted

## Context

Lynk needs a retrieval system that keeps document provenance, page citations,
collection permissions, review status, source quality, and research-run audit
records connected to the chunks used for answers. The system also needs
extensible metadata and semantic retrieval as its local corpus grows.

## Decision

Use a local PostgreSQL database with the pgvector extension as the long-term
source of truth for Lynk retrieval.

Frequently filtered values will use typed relational columns. Flexible,
evolving metadata, retrieval plans, and decision traces will use JSONB. Chunk
embeddings will use pgvector, and PostgreSQL full-text search will provide the
keyword component of hybrid retrieval.

The agent accesses the data through a restricted schema registry and
parameterized retrieval tools. It will not execute arbitrary model-generated
SQL.

## Alternatives considered

### Keep SQLite as the long-term RAG store

Rejected as the primary production store because the project needs a stronger
path for concurrent access, JSON indexing, full-text search, vector search,
schema migrations, and a demonstrable SQL retrieval architecture.

### Use a separate vector database as the source of truth

Rejected because relational evidence, metadata, audit records, and vectors
would be split across systems. PostgreSQL with pgvector keeps the first version
cohesive while providing sufficient local growth headroom.

## Consequences

- Local development uses Dockerized PostgreSQL and pgvector.
- The initial SQLite catalog has a documented migration path.
- Schema migrations, integration tests, and connection configuration become
  first-class project concerns.
- Private runtime data remains local and excluded from Git.
