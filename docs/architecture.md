# Architecture: milestone 1

## Goal

Establish a local, auditable document foundation before adding retrieval or a
language model. A document must be traceable back to its exact source file and
page before it can influence a research answer.

## Flow

1. The user chooses a local text, Markdown, or PDF file.
2. `DocumentIngestor` calculates a SHA-256 hash and copies the original into a
   private local data directory.
3. An extractor emits page-level text. PDFs use `pypdf`; pages without text are
   marked for OCR rather than silently treated as empty evidence.
4. An injected OCR engine can produce text for those pages. The initial
   production adapter uses the local `ocrmypdf` command when installed; tests
   use a fake engine.
5. `DocumentCatalog` stores the source, immutable copy location, hash,
   extraction status, and every extracted page in SQLite.

## Non-goals

This milestone does not embed, retrieve, index into RAG, call a model, or send
content to the web. Those are separate promotion-gated stages.

## Next milestones

1. Page-aware chunking and a local embedding adapter.
2. Vector plus keyword retrieval with collection and permission filters.
3. Review queue and approved-evidence promotion.
4. Topic-driven, policy-limited web research.
5. A local model adapter and OpenAI-compatible agent API for Open WebUI.

