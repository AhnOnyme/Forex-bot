from datetime import UTC, datetime
from unittest.mock import MagicMock

from forex_bot.broker.base import Broker
from forex_bot.data.prices import fetch_latest_candles
from forex_bot.models import Candle


def test_fetch_latest_candles_falls_back_to_stub_without_broker():
    candles = fetch_latest_candles(None, "EUR_USD", "M15", 10)

    assert len(candles) == 1


def test_fetch_latest_candles_delegates_to_broker():
    fake_candle = Candle(timestamp=datetime.now(UTC), open=1.1, high=1.2, low=1.0, close=1.15, volume=100)
    broker = MagicMock(spec=Broker)
    broker.get_candles.return_value = [fake_candle]

    result = fetch_latest_candles(broker, "EUR_USD", "M15", 10)

    broker.get_candles.assert_called_once_with("EUR_USD", "M15", 10)
    assert result == [fake_candle]
