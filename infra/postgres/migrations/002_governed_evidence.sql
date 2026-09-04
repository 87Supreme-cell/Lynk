-- Governed evidence lifecycle: run with the project's migration runner, not Docker init alone.

CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    content_hash TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    extraction_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, version_number),
    UNIQUE (document_id, content_hash)
);

CREATE TABLE collection_permissions (
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    principal_id TEXT NOT NULL,
    permission TEXT NOT NULL CHECK (permission IN ('retrieve', 'review', 'manage')),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (collection_id, principal_id, permission)
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    chunk_id UUID REFERENCES chunks(id) ON DELETE SET NULL,
    policy_version TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE chunks ADD COLUMN document_version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE chunks ADD COLUMN start_offset INTEGER NOT NULL DEFAULT 0;
ALTER TABLE chunks ADD COLUMN end_offset INTEGER NOT NULL DEFAULT 0;

CREATE INDEX collection_permissions_principal_idx ON collection_permissions (principal_id, collection_id);
CREATE INDEX audit_events_document_idx ON audit_events (document_id, created_at DESC);
