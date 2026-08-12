import pytest

from forex_bot.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        oanda_api_key=None,
        oanda_account_id=None,
        llm_api_key=None,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
