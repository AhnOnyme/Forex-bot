import pytest
from oandapyV20.exceptions import V20Error

from forex_bot.broker.oanda import OandaBroker, _parse_oanda_time
from forex_bot.config import Settings

CANDLES_RESPONSE = {
    "candles": [
        {
            "complete": True,
            "volume": 120,
            "time": "2024-01-05T13:30:00.000000000Z",
            "mid": {"o": "1.10000", "h": "1.10050", "l": "1.09950", "c": "1.10020"},
        }
    ],
    "granularity": "M15",
    "instrument": "EUR_USD",
}

ACCOUNT_RESPONSE = {"balance": "100000.0000", "currency": "USD", "id": "101-001-1234567-001"}


class FakeApiClient:
    def __init__(self, candles_response=None, account_response=None, raise_error=False):
        self._candles_response = candles_response
        self._account_response = account_response
        self._raise_error = raise_error

    def request(self, endpoint):
        if self._raise_error:
            raise V20Error(400, "boom")
        if type(endpoint).__name__ == "InstrumentsCandles":
            endpoint.response = self._candles_response
        elif type(endpoint).__name__ == "AccountSummary":
            endpoint.response = {"account": self._account_response}


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, oanda_api_key="key", oanda_account_id="acct", **overrides)


def test_refuses_to_start_outside_practice():
    with pytest.raises(RuntimeError):
        OandaBroker(_settings(oanda_environment="live"), api_client=FakeApiClient())


def test_get_candles_maps_response_to_models():
    broker = OandaBroker(_settings(), api_client=FakeApiClient(candles_response=CANDLES_RESPONSE))

    candles = broker.get_candles("EUR_USD", "M15", 1)

    assert len(candles) == 1
    candle = candles[0]
    assert candle.open == 1.10000
    assert candle.close == 1.10020
    assert candle.volume == 120
    assert candle.timestamp.year == 2024


def test_get_candles_wraps_v20_error():
    broker = OandaBroker(_settings(), api_client=FakeApiClient(raise_error=True))

    with pytest.raises(RuntimeError):
        broker.get_candles("EUR_USD", "M15", 1)


def test_get_account_summary_maps_response():
    broker = OandaBroker(_settings(), api_client=FakeApiClient(account_response=ACCOUNT_RESPONSE))

    summary = broker.get_account_summary()

    assert summary["currency"] == "USD"
    assert summary["balance"] == "100000.0000"


def test_parse_oanda_time_truncates_nanoseconds():
    parsed = _parse_oanda_time("2024-01-05T13:30:00.000000000Z")
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 5
