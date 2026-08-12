import pytest
from pydantic import ValidationError

from forex_bot.config import Settings


def test_settings_default_environment_is_practice():
    settings = Settings(_env_file=None)
    assert settings.oanda_environment == "practice"


def test_settings_loads_explicit_values():
    settings = Settings(_env_file=None, oanda_api_key="abc", instrument="GBP_USD")
    assert settings.oanda_api_key == "abc"
    assert settings.instrument == "GBP_USD"


def test_settings_rejects_invalid_environment():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, oanda_environment="not-a-real-environment")
