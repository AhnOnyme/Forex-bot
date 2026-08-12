import pytest

from forex_bot.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        oanda_api_key="test-key",
        oanda_account_id="test-account",
        llm_api_key=None,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
