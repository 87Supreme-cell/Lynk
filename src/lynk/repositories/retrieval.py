"""Parameterized PostgreSQL retrieval constrained by Lynk's evidence policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Cursor(Protocol):
    def execute(self, query: str, parameters: tuple[object, ...]) -> None: ...

    def fetchall(self) -> list[dict[str, object]]: ...


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    principal_id: str
    limit: int = 12


class PostgresEvidenceRepository:
    """Return only evidence that SQL itself scopes to the requesting principal."""

    _QUERY = """
        SELECT chunks.id::text AS evidence_id, documents.id::text AS document_id,
               collections.id::text AS collection_id, documents.status,
               collections.access_scope, chunks.content AS excerpt,
               document_pages.page_number, documents.content_hash
        FROM chunks
        JOIN documents ON documents.id = chunks.document_id
        JOIN collections ON collections.id = documents.collection_id
        LEFT JOIN document_pages ON document_pages.id = chunks.page_id
        WHERE chunks.content_tsv @@ websearch_to_tsquery('english', %s)
          AND (
            (documents.status = 'approved' AND collections.access_scope = 'curated')
            OR (
                documents.status = 'private' AND collections.access_scope = 'private'
                AND EXISTS (
                    SELECT 1 FROM collection_permissions permissions
                    WHERE permissions.collection_id = collections.id
                      AND permissions.principal_id = %s
                      AND permissions.permission = 'retrieve'
                )
            )
          )
        ORDER BY ts_rank_cd(chunks.content_tsv, websearch_to_tsquery('english', %s)) DESC
        LIMIT %s
    """

    def search(self, cursor: Cursor, request: RetrievalRequest) -> list[dict[str, object]]:
        if not request.query.strip():
            raise ValueError("retrieval query cannot be blank")
        if not 1 <= request.limit <= 50:
            raise ValueError("retrieval limit must be between 1 and 50")
        cursor.execute(self._QUERY, (request.query, request.principal_id, request.query, request.limit))
        return cursor.fetchall()
