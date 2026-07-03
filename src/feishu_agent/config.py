from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    feishu_app_id: str = Field(default="", validation_alias="FEISHU_APP_ID")
    feishu_app_secret: SecretStr = Field(default=SecretStr(""), validation_alias="FEISHU_APP_SECRET")
    feishu_verification_token: SecretStr = Field(default=SecretStr(""), validation_alias="FEISHU_VERIFICATION_TOKEN")
    feishu_encrypt_key: SecretStr = Field(default=SecretStr(""), validation_alias="FEISHU_ENCRYPT_KEY")

    openai_api_key: SecretStr = Field(default=SecretStr(""), validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL")
    agent_model: str = Field(default="gpt-4.1-mini", validation_alias="AGENT_MODEL")
    agent_system_prompt: str = Field(
        default="你是企业飞书里的智能助手。回答要简洁、准确，并优先使用中文。",
        validation_alias="AGENT_SYSTEM_PROMPT",
    )

    request_timeout_seconds: float = Field(default=20.0, validation_alias="REQUEST_TIMEOUT_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
