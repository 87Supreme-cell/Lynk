"""Deterministic evidence policy. Models never make these decisions."""

from __future__ import annotations

from lynk.domain import AccessScope, EvidenceRecord, EvidenceStatus, PolicyDecision, ReviewDecision, ReviewStatus

POLICY_VERSION = "2026-09-03.1"


def authorize_retrieval(evidence: EvidenceRecord, principal_id: str) -> PolicyDecision:
    """Allow only approved curated evidence or explicitly granted private context."""
    if evidence.status is EvidenceStatus.REJECTED:
        return PolicyDecision(False, "rejected evidence is never retrievable")
    if evidence.status is EvidenceStatus.CANDIDATE:
        return PolicyDecision(False, "candidate evidence is review-only")
    if evidence.status is EvidenceStatus.APPROVED and evidence.access_scope is AccessScope.CURATED:
        return PolicyDecision(True, "approved curated evidence")
    if evidence.status is EvidenceStatus.PRIVATE and evidence.access_scope is AccessScope.PRIVATE:
        if principal_id in evidence.allowed_principals:
            return PolicyDecision(True, "explicit private-collection grant")
        return PolicyDecision(False, "missing private-collection grant")
    return PolicyDecision(False, "status and collection scope are incompatible")


def authorize_promotion(record: EvidenceRecord, review: ReviewDecision) -> PolicyDecision:
    """Require an explicit, policy-versioned human approval for promotion."""
    if record.status is not EvidenceStatus.CANDIDATE:
        return PolicyDecision(False, "only candidate evidence may be promoted")
    if review.evidence_id != record.evidence_id:
        return PolicyDecision(False, "review does not belong to this evidence")
    if review.status is not ReviewStatus.APPROVED:
        return PolicyDecision(False, "an explicit approved review is required")
    if not review.reviewer_id or not review.reason.strip():
        return PolicyDecision(False, "reviewer identity and decision reason are required")
    if review.policy_version != POLICY_VERSION:
        return PolicyDecision(False, "review was made under a different policy version")
    return PolicyDecision(True, "candidate may be atomically promoted")
