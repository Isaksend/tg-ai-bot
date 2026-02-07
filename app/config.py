from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, HttpUrl


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: SecretStr
    BASE_URL: HttpUrl
    WEBHOOK_PATH: str = "/telegram/webhook"

    # AI
    MODEL_NAME: str = "llama3"
    OLLAMA_URL: str = "http://localhost:11434"  # Для Docker обычно http://ollama:11434
    MAX_CONTEXT_MESSAGES: int = 10

    # Vision & Files
    MAX_IMAGE_MB: int = 10
    IMAGE_DIR: str = "data/images"

    # App
    ENV: str = "prod"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()