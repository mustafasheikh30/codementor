from pydantic_settings import BaseSettings, SettingsConfigDict


class SandboxSettings(BaseSettings):
    # Disabled by default for safety. Must be explicitly enabled.
    sandbox_enabled: bool = False
    sandbox_use_docker: bool = False
    sandbox_network_disabled: bool = True
    sandbox_default_time_limit_seconds: float = 2.0
    sandbox_default_memory_limit_mb: int = 256
    sandbox_max_output_bytes: int = 102_400
    sandbox_workdir_base: str = "/tmp/codementor-sandbox"
    # Image names only - never store credentials
    sandbox_docker_image_python: str = "python:3.12-slim"
    sandbox_docker_image_cpp: str = "gcc:13"
    sandbox_docker_image_java: str = "openjdk:21-slim"
    sandbox_docker_image_rust: str = "rust:1.82-slim"
    sandbox_docker_image_node: str = "node:22-slim"
    sandbox_docker_image_go: str = "golang:1.23"

    model_config = SettingsConfigDict(env_prefix="SANDBOX_", env_file=".env", extra="ignore")


sandbox_settings = SandboxSettings()
