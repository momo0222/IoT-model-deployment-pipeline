from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_path: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()