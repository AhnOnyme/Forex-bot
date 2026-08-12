import requests

from forex_bot.config import Settings
from forex_bot.data.news import fetch_latest_news

FF_PAYLOAD = [
    {
        "title": "CPI m/m",
        "country": "USD",
        "date": "2024-01-05T13:30:00-05:00",
        "impact": "High",
        "forecast": "0.2%",
        "previous": "0.1%",
    },
    {
        "title": "Retail Sales",
        "country": "GBP",
        "date": "2024-01-05T09:30:00+00:00",
        "impact": "Medium",
        "forecast": "0.1%",
        "previous": "0.0%",
    },
    {
        "title": "Bank Holiday",
        "country": "EUR",
        "date": "2024-01-05T00:00:00+00:00",
        "impact": "Holiday",
    },
]


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, instrument="EUR_USD", **overrides)


def test_fetch_latest_news_filters_by_instrument_and_maps_impact(monkeypatch):
    monkeypatch.setattr("forex_bot.data.news.requests.get", lambda *a, **k: FakeResponse(FF_PAYLOAD))

    items = fetch_latest_news(_settings())

    currencies = {item.currency for item in items}
    assert currencies == {"USD", "EUR"}  # GBP filtre car hors EUR_USD

    usd_item = next(i for i in items if i.currency == "USD")
    assert usd_item.impact == "high"

    eur_item = next(i for i in items if i.currency == "EUR")
    assert eur_item.impact == "low"  # "Holiday" -> "low"


def test_fetch_latest_news_falls_back_to_stub_on_network_error(monkeypatch):
    def _raise(*args, **kwargs):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr("forex_bot.data.news.requests.get", _raise)

    items = fetch_latest_news(_settings())

    assert len(items) == 1
    assert items[0].source == "stub"
