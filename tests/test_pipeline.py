from datetime import UTC, datetime

from forex_bot.models import NewsItem
from forex_bot.pipeline import ShutdownHandler, run_forever, run_once


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


def test_shutdown_handler_sets_requested_flag_on_signal():
    handler = ShutdownHandler()

    handler.request_shutdown(15, None)  # 15 = SIGTERM

    assert handler.requested is True


def test_run_forever_stops_once_shutdown_is_requested(settings, monkeypatch):
    calls = []
    monkeypatch.setattr("forex_bot.pipeline.run_once", lambda s: calls.append(1))

    shutdown = ShutdownHandler()

    def fake_sleep(seconds):
        shutdown.requested = True  # simule un Ctrl+C pendant l'attente

    loop_settings = settings.model_copy(update={"poll_interval_seconds": 5})

    run_forever(loop_settings, shutdown=shutdown, sleep_fn=fake_sleep)

    assert len(calls) == 1


def test_run_forever_continues_after_a_failed_cycle(settings, monkeypatch):
    calls = []
    shutdown = ShutdownHandler()

    def fake_run_once(s):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("panne temporaire")
        shutdown.requested = True

    monkeypatch.setattr("forex_bot.pipeline.run_once", fake_run_once)

    loop_settings = settings.model_copy(update={"poll_interval_seconds": 1})

    run_forever(loop_settings, shutdown=shutdown, sleep_fn=lambda s: None)

    assert len(calls) == 2
