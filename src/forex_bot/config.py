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
    llm_candle_window: int = 20  # nb de bougies envoyees dans le prompt (limite le cout/la taille)

    # Telegram notifications
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    # News / calendrier economique (flux ForexFactory, pas de cle requise)
    news_calendar_url: str = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    # Gestion du risque (etape 4)
    risk_stop_loss_pct: float = 0.005  # distance du stop-loss par rapport au prix d'entree (0.5%)
    risk_per_trade_pct: float = 0.01  # part max du solde du compte risquee par trade (1%)
    risk_news_blackout_minutes: int = 15  # pas de nouvel ordre autour d'une news a fort impact

    # App behavior
    log_level: str = "INFO"
    poll_interval_seconds: int = 300
    instrument: str = "EUR_USD"
    run_once_only: bool = False  # true = un seul cycle puis exit (debug/tests manuels)


@lru_cache
def get_settings() -> Settings:
    return Settings()
