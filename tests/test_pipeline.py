from forex_bot.pipeline import run_once


def test_run_once_completes_without_raising(settings):
    run_once(settings)
