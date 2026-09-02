"""PostgreSQL catalog adapter for the SQL-first retrieval architecture."""

from __future__ import annotations

import json
import os
from typing import Any

from lynk.models import IngestedDocument


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
            cursor.executemany(
                """INSERT INTO document_pages
                (document_id, page_number, content, needs_ocr, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb)""",
                [
                    (document.document_id, page.number, page.text, page.needs_ocr, "{}")
                    for page in document.pages
                ],
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
