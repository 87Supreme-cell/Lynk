import pytest

from lynk.repositories.retrieval import PostgresEvidenceRepository, RetrievalRequest


class FakeCursor:
    def __init__(self) -> None:
        self.query = ""
        self.parameters: tuple[object, ...] = ()

    def execute(self, query: str, parameters: tuple[object, ...]) -> None:
        self.query, self.parameters = query, parameters

    def fetchall(self) -> list[dict[str, object]]:
        return []


def test_retrieval_query_hard_codes_approved_or_explicitly_granted_private_scope() -> None:
    cursor = FakeCursor()
    PostgresEvidenceRepository().search(cursor, RetrievalRequest("security policy", "alice"))
    assert "documents.status = 'approved'" in cursor.query
    assert "documents.status = 'private'" in cursor.query
    assert "collection_permissions" in cursor.query
    assert cursor.parameters == ("security policy", "alice", "security policy", 12)


def test_retrieval_rejects_unbounded_or_empty_requests() -> None:
    repository = PostgresEvidenceRepository()
    with pytest.raises(ValueError, match="blank"):
        repository.search(FakeCursor(), RetrievalRequest(" ", "alice"))
    with pytest.raises(ValueError, match="between"):
        repository.search(FakeCursor(), RetrievalRequest("q", "alice", 51))
