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

POSITIONS_RESPONSE = [
    {"instrument": "EUR_USD", "long": {"units": "100"}, "short": {"units": "0"}},
]

ORDER_RESPONSE = {"orderFillTransaction": {"id": "42", "instrument": "EUR_USD"}}


class FakeApiClient:
    def __init__(
        self,
        candles_response=None,
        account_response=None,
        positions_response=None,
        order_response=None,
        raise_error=False,
    ):
        self._candles_response = candles_response
        self._account_response = account_response
        self._positions_response = positions_response
        self._order_response = order_response
        self._raise_error = raise_error
        self.last_endpoint = None

    def request(self, endpoint):
        self.last_endpoint = endpoint
        if self._raise_error:
            raise V20Error(400, "boom")
        endpoint_type = type(endpoint).__name__
        if endpoint_type == "InstrumentsCandles":
            endpoint.response = self._candles_response
        elif endpoint_type == "AccountSummary":
            endpoint.response = {"account": self._account_response}
        elif endpoint_type == "OpenPositions":
            endpoint.response = {"positions": self._positions_response}
        elif endpoint_type == "OrderCreate":
            endpoint.response = self._order_response


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


def test_get_open_positions_maps_response():
    broker = OandaBroker(_settings(), api_client=FakeApiClient(positions_response=POSITIONS_RESPONSE))

    positions = broker.get_open_positions()

    assert positions == POSITIONS_RESPONSE


def test_place_order_sends_units_and_stop_loss():
    fake_client = FakeApiClient(order_response=ORDER_RESPONSE)
    broker = OandaBroker(_settings(), api_client=fake_client)

    result = broker.place_order("EUR_USD", units=-1000, stop_loss=1.0945)

    assert result == ORDER_RESPONSE
    sent_order = fake_client.last_endpoint.data["order"]
    assert sent_order["instrument"] == "EUR_USD"
    assert sent_order["units"] == "-1000"
    assert sent_order["stopLossOnFill"]["price"] == "1.09450"


def test_place_order_wraps_v20_error():
    broker = OandaBroker(_settings(), api_client=FakeApiClient(raise_error=True))

    with pytest.raises(RuntimeError):
        broker.place_order("EUR_USD", units=1000)


def test_parse_oanda_time_truncates_nanoseconds():
    parsed = _parse_oanda_time("2024-01-05T13:30:00.000000000Z")
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 5
