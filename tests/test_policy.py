from lynk.domain import AccessScope, EvidenceRecord, EvidenceStatus, ReviewDecision, ReviewStatus
from lynk.policy import POLICY_VERSION, authorize_promotion, authorize_retrieval


def evidence(status: EvidenceStatus, scope: AccessScope, principals: frozenset[str] = frozenset()) -> EvidenceRecord:
    return EvidenceRecord("chunk-1", "doc-1", "collection-1", status, scope, "excerpt", 1, "hash", principals)


def test_candidate_and_rejected_evidence_never_reach_answer_retrieval() -> None:
    assert not authorize_retrieval(evidence(EvidenceStatus.CANDIDATE, AccessScope.CANDIDATE), "alice").allowed
    assert not authorize_retrieval(evidence(EvidenceStatus.REJECTED, AccessScope.CURATED), "alice").allowed


def test_private_evidence_requires_an_explicit_grant() -> None:
    private = evidence(EvidenceStatus.PRIVATE, AccessScope.PRIVATE, frozenset({"alice"}))
    assert authorize_retrieval(private, "alice").allowed
    assert not authorize_retrieval(private, "bob").allowed


def test_promotion_requires_an_explicit_current_policy_human_review() -> None:
    record = evidence(EvidenceStatus.CANDIDATE, AccessScope.CANDIDATE)
    rejected = ReviewDecision("chunk-1", ReviewStatus.REJECTED, "alice", POLICY_VERSION, "not authoritative")
    approved = ReviewDecision("chunk-1", ReviewStatus.APPROVED, "alice", POLICY_VERSION, "official source")
    assert not authorize_promotion(record, rejected).allowed
    assert authorize_promotion(record, approved).allowed
