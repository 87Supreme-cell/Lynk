"""SQLite persistence for locally stored documents and extracted pages."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from lynk.ingestion import utc_now
from lynk.models import IngestedDocument


class DocumentCatalog:
    """Local metadata catalog; it does not create embeddings or RAG entries."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def add(self, document: IngestedDocument) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO documents
                (id, original_name, source_path, stored_path, content_hash, media_type, extraction_status, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (document.document_id, document.original_name, str(document.source_path), str(document.stored_path),
                 document.content_hash, document.media_type, document.extraction_status, utc_now()),
            )
            connection.executemany(
                "INSERT INTO pages (document_id, page_number, text, needs_ocr) VALUES (?, ?, ?, ?)",
                [(document.document_id, page.number, page.text, page.needs_ocr) for page in document.pages],
            )

    def list_documents(self) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, original_name, content_hash, extraction_status, ingested_at FROM documents ORDER BY ingested_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, original_name TEXT NOT NULL, source_path TEXT NOT NULL,
                    stored_path TEXT NOT NULL, content_hash TEXT NOT NULL, media_type TEXT NOT NULL,
                    extraction_status TEXT NOT NULL, ingested_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pages (
                    document_id TEXT NOT NULL REFERENCES documents(id), page_number INTEGER NOT NULL,
                    text TEXT NOT NULL, needs_ocr INTEGER NOT NULL, PRIMARY KEY (document_id, page_number)
                );"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

