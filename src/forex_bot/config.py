from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OANDA (paper trading account)
    oanda_api_key: str | None = None
    oanda_account_id: str | None = None
    oanda_environment: Literal["practice", "live"] = "practice"
    oanda_granularity: str = "M15"
    oanda_candle_count: int = 50

    # LLM brain (OpenRouter, Qwen model)
    llm_api_key: str | None = None
    llm_model: str = "qwen/qwen-2.5-72b-instruct"
    llm_base_url: str = "https://openrouter.ai/api/v1"

    # Telegram notifications
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # News / calendrier economique (flux ForexFactory, pas de cle requise)
    news_calendar_url: str = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    # App behavior
    log_level: str = "INFO"
    poll_interval_seconds: int = 300
    instrument: str = "EUR_USD"


@lru_cache
def get_settings() -> Settings:
    return Settings()
