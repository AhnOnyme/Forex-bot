from datetime import UTC, datetime

from forex_bot.models import NewsItem
from forex_bot.pipeline import run_once


def test_run_once_completes_without_raising(settings, monkeypatch):
    # Evite tout appel reseau reel au calendrier ForexFactory dans ce smoke test.
    monkeypatch.setattr(
        "forex_bot.pipeline.fetch_latest_news",
        lambda _settings: [
            NewsItem(
                timestamp=datetime.now(UTC),
                title="test",
                currency="USD",
                impact="low",
                source="test",
            )
        ],
    )

    run_once(settings)
