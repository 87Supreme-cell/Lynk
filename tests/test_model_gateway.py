from typing import Any

import pytest

from lynk.model_gateway import ModelConfig, create_local_chat_model


class FakeHttp:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.requests: list[tuple[str, str, dict[str, Any]]] = []

    def get(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        self.requests.append(("GET", url, headers))
        return self.responses.pop(0)

    def post(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        self.requests.append(("POST", url, body))
        return self.responses.pop(0)


def test_ollama_adapter_lists_and_calls_configured_model() -> None:
    http = FakeHttp([{"models": [{"name": "gemma3:latest"}]}, {"message": {"content": "Grounded."}}])
    model = create_local_chat_model(ModelConfig("ollama", "http://local", "gemma3:latest"), http)

    assert model.list_models() == ("gemma3:latest",)
    assert model.complete("Summarize this evidence.") == "Grounded."
    assert http.requests[1][2]["options"] == {"temperature": 0.1, "top_p": 0.85}


def test_open_webui_adapter_uses_explicit_bearer_key() -> None:
    http = FakeHttp([{"data": [{"id": "qwen3:latest"}]}, {"choices": [{"message": {"content": "Cited."}}]}])
    model = create_local_chat_model(
        ModelConfig("open_webui", "http://ui", "qwen3:latest", api_key="local-key"), http
    )

    assert model.list_models() == ("qwen3:latest",)
    assert model.complete("What changed?") == "Cited."
    assert http.requests[0][2] == {"Authorization": "Bearer local-key"}


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        create_local_chat_model(ModelConfig("cloud", "http://local", "gemma"))
