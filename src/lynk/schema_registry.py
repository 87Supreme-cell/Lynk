"""Restricted retrieval resources exposed to a future model planner."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalResource:
    """A queryable evidence resource and the filters it permits."""

    name: str
    purpose: str
    allowed_filters: frozenset[str]
    access_scope: str


class RetrievalSchemaRegistry:
    """Maps retrieval intent to approved resources; never emits raw SQL."""

    _resources = (
        RetrievalResource(
            "approved_evidence",
            "Cited, approved evidence for research answers.",
            frozenset({"collection", "source_tier", "published_after", "topic_tags"}),
            "curated",
        ),
        RetrievalResource(
            "private_context",
            "User-authorized personal documents for grounding.",
            frozenset({"collection", "document_id", "topic_tags"}),
            "private",
        ),
        RetrievalResource(
            "candidate_evidence",
            "Unapproved evidence available only for review.",
            frozenset({"collection", "source_tier", "status"}),
            "candidate",
        ),
    )

    def describe(self) -> tuple[RetrievalResource, ...]:
        """Return model-safe schema descriptions without database credentials."""
        return self._resources

    def validate_filters(self, resource_name: str, filters: dict[str, object]) -> None:
        """Reject filters outside a resource's explicitly approved contract."""
        resource = next((item for item in self._resources if item.name == resource_name), None)
        if resource is None:
            raise ValueError(f"unknown retrieval resource: {resource_name}")
        rejected = set(filters) - resource.allowed_filters
        if rejected:
            raise ValueError(f"unsupported filters for {resource_name}: {sorted(rejected)}")
