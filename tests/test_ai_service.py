import httpx
import pytest
from pydantic import SecretStr

from app.ai import service
from app.core.config import settings


def configure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ai_api_key", SecretStr("test-key"))
    monkeypatch.setattr(settings, "ai_base_url", "https://ai.example/v1")
    monkeypatch.setattr(settings, "ai_model", "test-model")


def test_hint_requires_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ai_api_key", SecretStr(""))
    monkeypatch.setattr(settings, "ai_model", "")

    with pytest.raises(service.AiNotConfigured):
        service.generate_hint(name="A", rating=800, tags=["math"], code="x", level=1)


def test_hint_sends_problem_context_and_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    configure(monkeypatch)
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "  Consider the parity.  "}}]},
        )

    hint = service.generate_hint(
        name="Watermelon",
        rating=800,
        tags=["math", "brute force"],
        code="print(1)",
        level=2,
        transport=httpx.MockTransport(handler),
    )

    assert hint == "Consider the parity."
    assert seen["url"] == "https://ai.example/v1/chat/completions"
    assert seen["auth"] == "Bearer test-key"
    body = str(seen["body"])
    assert "Watermelon" in body
    assert "Hint level: 2 of 3" in body
    assert "print(1)" in body


def test_hint_maps_provider_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    configure(monkeypatch)

    with pytest.raises(service.AiUpstreamError):
        service.generate_hint(
            name="A",
            rating=None,
            tags=[],
            code="x",
            level=1,
            transport=httpx.MockTransport(lambda request: httpx.Response(500)),
        )

    with pytest.raises(service.AiUpstreamError):
        service.generate_hint(
            name="A",
            rating=None,
            tags=[],
            code="x",
            level=1,
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={})),
        )
