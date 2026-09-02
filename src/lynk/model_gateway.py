"""Explicit local model adapters for Ollama and Open WebUI."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for a local, already-installed model runtime."""

    provider: str
    base_url: str
    model_name: str
    temperature: float = 0.1
    top_p: float = 0.85
    api_key: str | None = None

    @classmethod
    def from_environment(cls) -> ModelConfig:
        """Load deliberate model settings without providing cloud defaults."""
        return cls(
            provider=os.environ.get("LYNK_MODEL_PROVIDER", "ollama"),
            base_url=os.environ.get("LYNK_MODEL_BASE_URL", "http://localhost:11434").rstrip("/"),
            model_name=os.environ.get("LYNK_MODEL_NAME", ""),
            temperature=float(os.environ.get("LYNK_MODEL_TEMPERATURE", "0.1")),
            top_p=float(os.environ.get("LYNK_MODEL_TOP_P", "0.85")),
            api_key=os.environ.get("LYNK_MODEL_API_KEY") or None,
        )


class JsonHttpClient(Protocol):
    """Minimal injected HTTP boundary for model-runtime adapters."""

    def get(self, url: str, headers: dict[str, str]) -> dict[str, Any]: ...

    def post(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]: ...


class UrllibJsonHttpClient:
    """Standard-library JSON client; no model provider SDK is required."""

    def get(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        return self._request(Request(url, headers=headers))

    def post(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        request = Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", **headers},
            method="POST",
        )
        return self._request(request)

    @staticmethod
    def _request(request: Request) -> dict[str, Any]:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))


class LocalChatModel(Protocol):
    """Common model contract used by the future research planner."""

    def list_models(self) -> tuple[str, ...]: ...

    def complete(self, user_message: str, system_message: str = "") -> str: ...


class OllamaChatModel:
    """Adapter for an already-running local Ollama service."""

    def __init__(self, config: ModelConfig, http: JsonHttpClient | None = None) -> None:
        self.config = config
        self.http = http or UrllibJsonHttpClient()

    def list_models(self) -> tuple[str, ...]:
        payload = self.http.get(f"{self.config.base_url}/api/tags", {})
        return tuple(item["name"] for item in payload.get("models", []))

    def complete(self, user_message: str, system_message: str = "") -> str:
        self._require_model_name()
        messages = ([{"role": "system", "content": system_message}] if system_message else []) + [
            {"role": "user", "content": user_message}
        ]
        payload = self.http.post(
            f"{self.config.base_url}/api/chat",
            {
                "model": self.config.model_name,
                "messages": messages,
                "stream": False,
                "options": {"temperature": self.config.temperature, "top_p": self.config.top_p},
            },
            {},
        )
        return str(payload["message"]["content"])

    def _require_model_name(self) -> None:
        if not self.config.model_name or self.config.model_name.startswith("replace-with-"):
            raise ValueError("Set LYNK_MODEL_NAME to an installed Ollama model ID")


class OpenWebUIChatModel:
    """Adapter for a locally running Open WebUI chat-completions endpoint."""

    def __init__(self, config: ModelConfig, http: JsonHttpClient | None = None) -> None:
        self.config = config
        self.http = http or UrllibJsonHttpClient()

    def list_models(self) -> tuple[str, ...]:
        payload = self.http.get(f"{self.config.base_url}/api/models", self._headers())
        return tuple(item["id"] for item in payload.get("data", []))

    def complete(self, user_message: str, system_message: str = "") -> str:
        self._require_model_name()
        messages = ([{"role": "system", "content": system_message}] if system_message else []) + [
            {"role": "user", "content": user_message}
        ]
        payload = self.http.post(
            f"{self.config.base_url}/api/chat/completions",
            {
                "model": self.config.model_name,
                "messages": messages,
                "stream": False,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            },
            self._headers(),
        )
        return str(payload["choices"][0]["message"]["content"])

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.api_key}"} if self.config.api_key else {}

    def _require_model_name(self) -> None:
        if not self.config.model_name or self.config.model_name.startswith("replace-with-"):
            raise ValueError("Set LYNK_MODEL_NAME to a model ID exposed by Open WebUI")


def create_local_chat_model(config: ModelConfig, http: JsonHttpClient | None = None) -> LocalChatModel:
    """Construct the one explicitly configured local provider; never silently fall back to cloud."""
    if config.provider == "ollama":
        return OllamaChatModel(config, http)
    if config.provider == "open_webui":
        return OpenWebUIChatModel(config, http)
    raise ValueError(f"unsupported local model provider: {config.provider}")
