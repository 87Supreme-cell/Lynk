"""The only model-facing PostgreSQL retrieval path."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from lynk.domain import AccessScope, EvidenceRecord, EvidenceStatus
from lynk.policy import POLICY_VERSION, authorize_retrieval
from lynk.repositories.retrieval import PostgresEvidenceRepository, RetrievalRequest


@dataclass(frozen=True)
class RetrievedEvidence:
    evidence_id: str
    document_id: str
    document_name: str
    page_number: int | None
    text: str

    @property
    def citation(self) -> str:
        page = f", p. {self.page_number}" if self.page_number else ""
        return f"{self.document_name}{page}"


class GovernedPostgresRetriever:
    """Enforce SQL and Python policy before evidence reaches a model."""

    def __init__(self, database_url: str, repository: PostgresEvidenceRepository | None = None) -> None:
        if not database_url:
            raise ValueError("database_url is required for governed retrieval")
        self.database_url = database_url
        self.repository = repository or PostgresEvidenceRepository()

    @classmethod
    def from_environment(cls) -> "GovernedPostgresRetriever":
        return cls(os.environ.get("LYNK_DATABASE_URL", ""))

    def search(self, request: RetrievalRequest) -> list[RetrievedEvidence]:
        try:
            import psycopg
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PostgreSQL retrieval requires psycopg") from exc
        with psycopg.connect(self.database_url) as connection, connection.cursor(
            row_factory=psycopg.rows.dict_row
        ) as cursor:
            rows = self.repository.search(cursor, request)
            evidence: list[RetrievedEvidence] = []
            for row in rows:
                record = EvidenceRecord(
                    evidence_id=str(row["evidence_id"]), document_id=str(row["document_id"]),
                    collection_id=str(row["collection_id"]), status=EvidenceStatus(str(row["status"])),
                    access_scope=AccessScope(str(row["access_scope"])), excerpt=str(row["excerpt"]),
                    page_number=int(row["page_number"] or 0), content_hash=str(row["content_hash"]),
                    allowed_principals=frozenset({request.principal_id}),
                )
                decision = authorize_retrieval(record, request.principal_id)
                if not decision.allowed:
                    continue
                cursor.execute(
                    """INSERT INTO audit_events (event_type, principal_id, document_id, chunk_id, policy_version, details)
                    VALUES ('retrieval_authorized', %s, %s::uuid, %s::uuid, %s, %s::jsonb)""",
                    (request.principal_id, record.document_id, record.evidence_id, POLICY_VERSION,
                    json.dumps({"decision": decision.reason})),
                )
                evidence.append(RetrievedEvidence(record.evidence_id, record.document_id,
                    str(row["document_name"]), int(row["page_number"]) if row["page_number"] else None,
                    record.excerpt))
            return evidence
