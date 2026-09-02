# ADR 0004: SQL verification before agent drafting

**Status:** accepted

## Context

The first local retrieval-to-model smoke test found an empty result set even
though an ingested document contained relevant content. The model must not be
used to conceal, guess around, or diagnose an unverified retrieval layer.

## Decision

Build and verify the deterministic retrieval path before invoking a model:

1. Define the SQL query and allowed metadata filters.
2. Ingest a synthetic fixture with known pages and chunks.
3. Assert the expected chunk rows, scope filters, ranking behavior, and page
   citations through database integration tests.
4. Pass the verified evidence to the local model only after those checks pass.

The research planner receives a restricted evidence contract and does not have
raw database access or authority to repair retrieval failures by inventing an
answer.

## Alternatives considered

### Let the model compensate for missing retrieval

Rejected because it obscures data, permissions, ranking, and citation bugs and
creates unsupported answers.

### Build agent behavior before deterministic retrieval tests

Rejected because model output cannot demonstrate whether the underlying SQL
query actually retrieved correct, authorized evidence.

## Consequences

- Every new retrieval filter or ranking change requires fixture-backed SQL
  integration coverage.
- The project can demonstrate a clear separation between data engineering and
  model orchestration during interviews.
- Model evaluation measures synthesis quality after retrieval correctness is
  established, not in place of it.
