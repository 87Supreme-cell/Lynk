import pytest

from lynk.schema_registry import RetrievalSchemaRegistry


def test_registry_describes_restricted_retrieval_resources() -> None:
    resources = RetrievalSchemaRegistry().describe()

    assert {resource.name for resource in resources} == {
        "approved_evidence",
        "private_context",
        "candidate_evidence",
    }


def test_registry_rejects_unapproved_filters() -> None:
    with pytest.raises(ValueError, match="unsupported filters"):
        RetrievalSchemaRegistry().validate_filters("private_context", {"status": "approved"})
