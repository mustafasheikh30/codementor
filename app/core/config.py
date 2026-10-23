from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeMentor"
    database_url: str = "postgresql+psycopg://codementor:codementor@localhost:5432/codementor"

    # Codeforces OpenID Connect. Empty values disable sign-in instead of failing
    # application startup, so the rest of the API remains usable without credentials.
    codeforces_oidc_client_id: str = ""
    codeforces_oidc_client_secret: SecretStr = SecretStr("")
    codeforces_oidc_state_secret: SecretStr = SecretStr("")
    codeforces_oidc_redirect_uri: str = ""

    # OpenAI-compatible chat-completions provider. Empty key/model disables the
    # coach instead of failing startup or making unauthenticated outbound calls.
    ai_api_key: SecretStr = SecretStr("")
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = ""
    ai_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
