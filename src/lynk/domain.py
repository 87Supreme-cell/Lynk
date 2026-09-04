"""Domain records used to enforce Lynk's evidence lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class EvidenceStatus(StrEnum):
    """The only states an evidence record may occupy."""

    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"
    PRIVATE = "private"


class AccessScope(StrEnum):
    """Coarse collection visibility; permissions further restrict private data."""

    PRIVATE = "private"
    CURATED = "curated"
    CANDIDATE = "candidate"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class EvidenceRecord:
    """A retrieved candidate with the fields required for policy evaluation."""

    evidence_id: str
    document_id: str
    collection_id: str
    status: EvidenceStatus
    access_scope: AccessScope
    excerpt: str
    page_number: int
    content_hash: str
    allowed_principals: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ReviewDecision:
    """An explicit human review result, never a model recommendation."""

    evidence_id: str
    status: ReviewStatus
    reviewer_id: str
    policy_version: str
    reason: str


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class Chunk:
    """Page-local text span retaining citation and lifecycle provenance."""

    chunk_index: int
    page_number: int
    start_offset: int
    end_offset: int
    content: str
    document_id: str
    document_version: int
    content_hash: str
    status: EvidenceStatus
    access_scope: AccessScope
