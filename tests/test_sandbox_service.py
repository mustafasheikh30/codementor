import pytest

from app.sandbox import service
from app.sandbox.config import sandbox_settings


def test_sandbox_disabled_by_default() -> None:
    assert sandbox_settings.sandbox_enabled is False
    result = service.execute_code("python", "print('hello')")
    assert result.status == "disabled"
    assert result.stdout == ""


def test_sandbox_network_disabled_by_default() -> None:
    assert sandbox_settings.sandbox_network_disabled is True


def test_sandbox_rejects_unsupported_language_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sandbox_settings, "sandbox_enabled", True)
    with pytest.raises(service.SandboxError):
        service.execute_code("brainfuck", "++.")


def test_sandbox_resource_limits_configured() -> None:
    assert sandbox_settings.sandbox_default_time_limit_seconds >= 0.1
    assert sandbox_settings.sandbox_default_memory_limit_mb >= 32
    assert sandbox_settings.sandbox_max_output_bytes > 0


def test_sandbox_never_executes_on_host_when_disabled() -> None:
    # Explicitly ensure no execution happens
    result = service.execute_code("python3", "import os; os.system('echo hacked')")
    assert result.status == "disabled"
    assert result.exit_code is None
