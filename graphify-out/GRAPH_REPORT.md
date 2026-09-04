# Graph Report - .  (2026-09-03)

## Corpus Check
- Corpus is ~9,498 words - fits in a single context window. You may not need a graph.

## Summary
- 248 nodes · 404 edges · 21 communities (12 shown, 9 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 69 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20

## God Nodes (most connected - your core abstractions)
1. `DocumentIngestor` - 14 edges
2. `IngestedDocument` - 14 edges
3. `main()` - 11 edges
4. `create_local_chat_model()` - 11 edges
5. `DocumentCatalog` - 10 edges
6. `ModelConfig` - 10 edges
7. `LocalChatModel` - 10 edges
8. `ExtractedPage` - 10 edges
9. `LocalResearchPlanner` - 10 edges
10. `RetrievalSchemaRegistry` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Verified Evidence Contract` --semantically_similar_to--> `SQL-First Retrieval Verification`  [INFERRED] [semantically similar]
  docs/decisions/0004-sql-verification-before-agent-drafting.md → AGENTS.md
- `SQL-First pgvector Retrieval` --semantically_similar_to--> `PostgreSQL pgvector Store`  [INFERRED] [semantically similar]
  docs/decisions/0002-sql-first-pgvector-retrieval.md → README.md
- `Evidence Lifecycle` --conceptually_related_to--> `Collection Permissions`  [INFERRED]
  docs/evidence-lifecycle.md → infra/postgres/migrations/002_governed_evidence.sql
- `Evidence Lifecycle` --conceptually_related_to--> `Document Versions`  [INFERRED]
  docs/evidence-lifecycle.md → infra/postgres/migrations/002_governed_evidence.sql
- `Answer Eligibility` --conceptually_related_to--> `Audit Events`  [INFERRED]
  docs/policy-contract.md → infra/postgres/migrations/002_governed_evidence.sql

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Governed Evidence Flow** — docs_evidence_lifecycle, docs_policy_contract_answer_eligibility, infra_postgres_migrations_002_collection_permissions, infra_postgres_migrations_002_audit_events [INFERRED 0.85]
- **Verified Grounded Drafting** — agents_sql_first_retrieval_verification, docs_decisions_0004_verified_evidence_contract, docs_build_log_local_retrieval_to_model_drafting, readme_local_evidence_drafting [INFERRED 0.85]

## Communities (21 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.09
Nodes (21): Request, create_local_chat_model(), JsonHttpClient, ModelConfig, OllamaChatModel, OpenWebUIChatModel, Any, Explicit local model adapters for Ollama and Open WebUI. (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (20): LocalChatModel, Protocol, Common model contract used by the future research planner., EvidenceRetriever, LocalResearchPlanner, Protocol, Evidence-first research drafting using a local model and approved retrieval., The limited retrieval contract available to the research planner. (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (20): SQLite persistence for locally stored documents and extracted pages., DocumentIngestor, OcrEngine, OCRmyPDFEngine, Path, Protocol, PypdfExtractor, Safe, local document ingestion with page-level provenance. (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (26): AccessScope, Chunk, EvidenceRecord, EvidenceStatus, PolicyDecision, Domain records used to enforce Lynk's evidence lifecycle., The only states an evidence record may occupy., Coarse collection visibility; permissions further restrict private data. (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (19): chunk_page(), PageChunk, Deterministic, page-aware chunks for retrieval and page citations., A chunk that retains the page from which it was extracted., Split one page at paragraph boundaries without crossing page citations., choose_document_path(), main(), Path (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.14
Nodes (12): PostgresRetriever, Restricted PostgreSQL keyword retrieval with provenance-rich results., Search only schema-registered evidence resources with bound SQL values., Restricted retrieval resources exposed to a future model planner., A queryable evidence resource and the filters it permits., Maps retrieval intent to approved resources; never emits raw SQL., Return model-safe schema descriptions without database credentials., Reject filters outside a resource's explicitly approved contract. (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.20
Nodes (9): Cursor, PostgresEvidenceRepository, Protocol, Parameterized PostgreSQL retrieval constrained by Lynk's evidence policy., Return only evidence that SQL itself scopes to the requesting principal., RetrievalRequest, FakeCursor, test_retrieval_query_hard_codes_approved_or_explicitly_granted_private_scope() (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (6): Connection, DocumentCatalog, Path, Local metadata catalog; it does not create embeddings or RAG entries., Return an ISO-8601 UTC timestamp for persisted provenance., utc_now()

### Community 8 - "Community 8"
Cohesion: 0.24
Nodes (10): Governed Retrieval Enforcement Foundation, Offline Resilience, Evidence Lifecycle, Answer Eligibility, Audit Events, Chunk Citation Offsets, Collection Permissions, Document Versions (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.39
Nodes (6): FakeOcr, Path, test_blank_pdf_is_preserved_and_flagged_for_ocr(), test_choose_document_path_uses_native_picker_result(), test_ingest_text_preserves_source_and_hash(), test_rejects_unsupported_document_types()

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (3): SQL-First Retrieval Verification, Local Retrieval-to-Model Drafting, Verified Evidence Contract

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (3): SQL-First pgvector Retrieval, Lynk, PostgreSQL pgvector Store

## Knowledge Gaps
- **6 isolated node(s):** `lynk`, `Lynk`, `Milestone One Ingestion`, `Local Retrieval-to-Model Drafting`, `DocumentIngestor` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `IngestedDocument` connect `Community 2` to `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Why does `DocumentIngestor` connect `Community 2` to `Community 9`, `Community 4`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `DocumentIngestor` (e.g. with `main()` and `ExtractedPage`) actually correct?**
  _`DocumentIngestor` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `IngestedDocument` (e.g. with `DocumentCatalog` and `DocumentIngestor`) actually correct?**
  _`IngestedDocument` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `main()` (e.g. with `DocumentCatalog` and `DocumentIngestor`) actually correct?**
  _`main()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `create_local_chat_model()` (e.g. with `main()` and `test_ollama_adapter_lists_and_calls_configured_model()`) actually correct?**
  _`create_local_chat_model()` has 4 INFERRED edges - model-reasoned connections that need verification._