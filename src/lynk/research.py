"""Evidence-first research drafting using a local model and approved retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lynk.model_gateway import LocalChatModel
from lynk.retrieval import RetrievedEvidence


class EvidenceRetriever(Protocol):
    """The limited retrieval contract available to the research planner."""

    def search(self, question: str, resource_name: str = "private_context") -> list[RetrievedEvidence]: ...


@dataclass(frozen=True)
class ResearchDraft:
    """An unapproved draft with the evidence made available to the local model."""

    question: str
    answer: str
    evidence: tuple[RetrievedEvidence, ...]


class LocalResearchPlanner:
    """Draft cited answers from retrieved evidence; it does not promote RAG content."""

    def __init__(self, model: LocalChatModel, retriever: EvidenceRetriever) -> None:
        self.model = model
        self.retriever = retriever

    def draft(self, question: str, resource_name: str = "private_context") -> ResearchDraft:
        """Retrieve approved scope first, then ask the model for a citation-bound draft."""
        evidence = tuple(self.retriever.search(question, resource_name))
        if not evidence:
            return ResearchDraft(
                question,
                "I could not find sufficient evidence in the authorized local collection.",
                evidence,
            )
        sources = "\n\n".join(
            f"[S{index}] {item.citation}\n{item.text}" for index, item in enumerate(evidence, start=1)
        )
        system_message = (
            "You are Lynk, a local evidence-governed research assistant. Use only the supplied evidence. "
            "Do not reveal private chain-of-thought. Return concise findings, uncertainty, and cite every "
            "material claim using [S1], [S2], and so on. If the evidence is insufficient, say so."
        )
        prompt = f"Question: {question}\n\nAuthorized evidence:\n{sources}\n\nDraft a cited answer."
        return ResearchDraft(question, self.model.complete(prompt, system_message), evidence)
