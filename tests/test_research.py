from lynk.research import LocalResearchPlanner
from lynk.governed_retrieval import RetrievedEvidence
from lynk.repositories.retrieval import RetrievalRequest


class FakeModel:
    def __init__(self) -> None:
        self.prompt = ""
        self.system_message = ""

    def list_models(self) -> tuple[str, ...]:
        return ()

    def complete(self, user_message: str, system_message: str = "") -> str:
        self.prompt = user_message
        self.system_message = system_message
        return "The document supports this claim. [S1]"


class FakeRetriever:
    def search(self, request: RetrievalRequest) -> list[RetrievedEvidence]:
        assert request.query == "What does the note say?"
        assert request.principal_id == "alice"
        return [RetrievedEvidence("chunk", "doc", "note.md", 2, "The note contains evidence.")]


def test_planner_only_uses_retrieved_evidence_and_requests_citations() -> None:
    model = FakeModel()

    draft = LocalResearchPlanner(model, FakeRetriever()).draft("What does the note say?", "alice")

    assert draft.answer.endswith("[S1]")
    assert "[S1] note.md, p. 2" in model.prompt
    assert "Do not reveal private chain-of-thought" in model.system_message


def test_planner_reports_when_no_authorized_evidence_is_found() -> None:
    class EmptyRetriever:
        def search(self, request: RetrievalRequest) -> list[RetrievedEvidence]:
            return []

    draft = LocalResearchPlanner(FakeModel(), EmptyRetriever()).draft("Missing?", "alice")

    assert "could not find sufficient evidence" in draft.answer


def test_planner_rejects_drafts_with_invented_or_missing_citations() -> None:
    class InvalidModel(FakeModel):
        def complete(self, user_message: str, system_message: str = "") -> str:
            return "Unsupported assertion. [S99]"

    draft = LocalResearchPlanner(InvalidModel(), FakeRetriever()).draft("What does the note say?", "alice")

    assert "citation-valid" in draft.answer
