"""Restricted PostgreSQL keyword retrieval with provenance-rich results."""

from __future__ import annotations

import os
from dataclasses import dataclass

from lynk.schema_registry import RetrievalSchemaRegistry


@dataclass(frozen=True)
class RetrievedEvidence:
    """A retrieved chunk with the citation data needed by a draft answer."""

    chunk_id: str
    document_id: str
    document_name: str
    page_number: int | None
    text: str
    score: float

    @property
    def citation(self) -> str:
        """Return a human-readable page citation for the evidence item."""
        page = f", p. {self.page_number}" if self.page_number else ""
        return f"{self.document_name}{page}"


class PostgresRetriever:
    """Search only schema-registered evidence resources with bound SQL values."""

    def __init__(self, database_url: str, registry: RetrievalSchemaRegistry | None = None) -> None:
        if not database_url:
            raise ValueError("database_url is required for PostgreSQL retrieval")
        self.database_url = database_url
        self.registry = registry or RetrievalSchemaRegistry()

    @classmethod
    def from_environment(cls) -> PostgresRetriever:
        """Create retrieval from the explicit local database connection."""
        return cls(os.environ.get("LYNK_DATABASE_URL", ""))

    def search(
        self,
        question: str,
        resource_name: str = "private_context",
        filters: dict[str, object] | None = None,
        limit: int = 6,
    ) -> list[RetrievedEvidence]:
        """Return top keyword matches after enforcing resource and filter policy."""
        if not question.strip():
            raise ValueError("question must not be empty")
        if not 1 <= limit <= 20:
            raise ValueError("limit must be between 1 and 20")
        filters = filters or {}
        self.registry.validate_filters(resource_name, filters)
        resource = next(item for item in self.registry.describe() if item.name == resource_name)
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover - dependency contract
            raise RuntimeError("PostgreSQL retrieval requires psycopg") from exc

        where = ["c.access_scope = %s"]
        values: list[object] = [resource.access_scope]
        status = {"private": "private", "curated": "approved", "candidate": "candidate"}[resource.access_scope]
        where.append("d.status = %s")
        values.append(status)
        if "collection" in filters:
            where.append("c.name = %s")
            values.append(filters["collection"])
        if "document_id" in filters:
            where.append("d.id = %s")
            values.append(filters["document_id"])
        if "source_tier" in filters:
            where.append("d.source_tier = %s")
            values.append(filters["source_tier"])
        if "published_after" in filters:
            where.append("d.published_at >= %s")
            values.append(filters["published_after"])
        if "status" in filters:
            where.append("d.status = %s")
            values.append(filters["status"])
        if "topic_tags" in filters:
            where.append("d.metadata @> %s::jsonb")
            values.append('{"topic_tags": ' + str(filters["topic_tags"]).replace("'", '"') + "}")

        statement = f"""
            WITH query_terms AS (
                SELECT to_tsquery(
                    'english', array_to_string(tsvector_to_array(to_tsvector('english', %s)), ' | ')
                ) AS value
            )
            SELECT ch.id::text AS chunk_id, d.id::text AS document_id, d.original_name, p.page_number, ch.content,
                   ts_rank(ch.content_tsv, query_terms.value) AS score
            FROM chunks AS ch
            JOIN documents AS d ON d.id = ch.document_id
            JOIN collections AS c ON c.id = d.collection_id
            LEFT JOIN document_pages AS p ON p.id = ch.page_id
            CROSS JOIN query_terms
            WHERE {' AND '.join(where)}
              AND ch.content_tsv @@ query_terms.value
            ORDER BY score DESC, d.ingested_at DESC
            LIMIT %s
        """
        parameters = [question, *values, limit]
        with (
            psycopg.connect(self.database_url) as connection,
            connection.cursor(row_factory=psycopg.rows.dict_row) as cursor,
        ):
            cursor.execute(statement, parameters)
            return [
                RetrievedEvidence(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    document_name=row["original_name"],
                    page_number=row["page_number"],
                    text=row["content"],
                    score=float(row["score"]),
                )
                for row in cursor.fetchall()
            ]
