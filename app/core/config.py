from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeMentor"
    database_url: str = "postgresql+psycopg://codementor:codementor@localhost:5432/codementor"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
