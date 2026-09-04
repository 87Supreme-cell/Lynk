"""PostgreSQL catalog adapter for the SQL-first retrieval architecture."""

from __future__ import annotations

import json
import os
from typing import Any

from lynk.domain import AccessScope, EvidenceStatus
from lynk.models import IngestedDocument
from lynk.services.chunking import PageChunker


class PostgresDocumentCatalog:
    """Persist ingested documents and page evidence in local PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("database_url is required for PostgreSQL storage")
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> PostgresDocumentCatalog:
        """Create a catalog from the intentionally explicit local database URL."""
        return cls(os.environ.get("LYNK_DATABASE_URL", ""))

    def add(
        self,
        document: IngestedDocument,
        collection_name: str = "private_context",
        metadata: dict[str, Any] | None = None,
        principal_id: str = "local-owner",
    ) -> None:
        """Store provenance and extracted pages in an existing pgvector schema."""
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - dependency contract
            raise RuntimeError("PostgreSQL storage requires psycopg; install project dependencies") from exc
        document_metadata = {"source_type": "user_upload", **(metadata or {})}
        with psycopg.connect(self.database_url) as connection, connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO collections (name, purpose, access_scope)
                VALUES (%s, %s, 'private') ON CONFLICT (name) DO NOTHING""",
                (collection_name, "User-authorized personal documents for grounding."),
            )
            cursor.execute("SELECT id FROM collections WHERE name = %s", (collection_name,))
            collection_id = cursor.fetchone()[0]
            cursor.execute(
                """INSERT INTO collection_permissions (collection_id, principal_id, permission)
                VALUES (%s, %s, 'retrieve') ON CONFLICT DO NOTHING""",
                (collection_id, principal_id),
            )
            cursor.execute(
                """INSERT INTO documents
                (id, collection_id, original_name, source_path, stored_path, content_hash,
                 media_type, status, extraction_status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'private', %s, %s::jsonb)""",
                (
                    document.document_id,
                    collection_id,
                    document.original_name,
                    str(document.source_path),
                    str(document.stored_path),
                    document.content_hash,
                    document.media_type,
                    document.extraction_status,
                    json.dumps(document_metadata),
                ),
            )
            cursor.execute(
                """INSERT INTO document_versions (document_id, version_number, content_hash, stored_path, extraction_status)
                VALUES (%s, 1, %s, %s, %s)""",
                (document.document_id, document.content_hash, str(document.stored_path), document.extraction_status),
            )
            page_ids: dict[int, object] = {}
            for page in document.pages:
                cursor.execute(
                    """INSERT INTO document_pages
                    (document_id, page_number, content, needs_ocr, metadata)
                    VALUES (%s, %s, %s, %s, %s::jsonb) RETURNING id""",
                    (document.document_id, page.number, page.text, page.needs_ocr, "{}"),
                )
                page_ids[page.number] = cursor.fetchone()[0]
            for chunk in PageChunker().chunk(document, 1, EvidenceStatus.PRIVATE, AccessScope.PRIVATE):
                cursor.execute(
                    """INSERT INTO chunks
                    (document_id, page_id, chunk_index, content, metadata, document_version, start_offset, end_offset)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s)""",
                    (document.document_id, page_ids[chunk.page_number], chunk.chunk_index, chunk.content,
                     json.dumps({"page_number": chunk.page_number, "content_hash": chunk.content_hash,
                                 "status": chunk.status, "access_scope": chunk.access_scope}),
                     chunk.document_version, chunk.start_offset, chunk.end_offset),
                )

    def list_documents(self) -> list[dict[str, str]]:
        """Return safe, catalog-level document details without content text."""
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - dependency contract
            raise RuntimeError("PostgreSQL storage requires psycopg; install project dependencies") from exc
        with (
            psycopg.connect(self.database_url) as connection,
            connection.cursor(row_factory=psycopg.rows.dict_row) as cursor,
        ):
            cursor.execute(
                """SELECT id::text, original_name, content_hash, extraction_status,
                ingested_at::text FROM documents ORDER BY ingested_at DESC"""
            )
            return list(cursor.fetchall())
