CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    purpose TEXT NOT NULL,
    access_scope TEXT NOT NULL CHECK (access_scope IN ('private', 'curated', 'candidate')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    collection_id UUID NOT NULL REFERENCES collections(id),
    original_name TEXT NOT NULL,
    source_path TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    source_url TEXT,
    content_hash TEXT NOT NULL,
    media_type TEXT NOT NULL,
    source_tier SMALLINT,
    status TEXT NOT NULL CHECK (status IN ('candidate', 'approved', 'rejected', 'private')),
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    extraction_status TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (collection_id, content_hash)
);

CREATE TABLE document_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL CHECK (page_number > 0),
    content TEXT NOT NULL,
    needs_ocr BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (document_id, page_number)
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_id UUID REFERENCES document_pages(id) ON DELETE SET NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding vector,
    embedding_model TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE research_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    scope JSONB NOT NULL DEFAULT '{}'::jsonb,
    retrieval_plan JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('planned', 'running', 'completed', 'blocked')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE retrieval_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    research_run_id UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    retrieval_score DOUBLE PRECISION NOT NULL,
    rationale JSONB NOT NULL DEFAULT '{}'::jsonb,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    decision_trace JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_at TIMESTAMPTZ,
    CHECK (document_id IS NOT NULL OR chunk_id IS NOT NULL)
);

CREATE TABLE retrieval_schema_registry (
    resource_name TEXT PRIMARY KEY,
    purpose TEXT NOT NULL,
    allowed_filters JSONB NOT NULL,
    access_scope TEXT NOT NULL
);

INSERT INTO retrieval_schema_registry (resource_name, purpose, allowed_filters, access_scope) VALUES
    ('approved_evidence', 'Cited, approved evidence for research answers',
     '["collection", "source_tier", "published_after", "topic_tags"]'::jsonb, 'curated'),
    ('private_context', 'User-authorized personal documents for grounding',
     '["collection", "document_id", "topic_tags"]'::jsonb, 'private'),
    ('candidate_evidence', 'Unapproved material available for review only',
     '["collection", "source_tier", "status"]'::jsonb, 'candidate')
ON CONFLICT (resource_name) DO NOTHING;

CREATE INDEX documents_collection_status_idx ON documents (collection_id, status, published_at DESC);
CREATE INDEX documents_metadata_idx ON documents USING GIN (metadata);
CREATE INDEX document_pages_document_idx ON document_pages (document_id, page_number);
CREATE INDEX chunks_document_idx ON chunks (document_id, chunk_index);
CREATE INDEX chunks_metadata_idx ON chunks USING GIN (metadata);
CREATE INDEX chunks_content_tsv_idx ON chunks USING GIN (content_tsv);
CREATE INDEX retrieval_events_run_idx ON retrieval_events (research_run_id, retrieval_score DESC);
