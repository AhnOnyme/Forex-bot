from datetime import UTC, datetime, timedelta

import pytest

from forex_bot.broker.base import Broker
from forex_bot.config import Settings
from forex_bot.models import Candle, Decision, NewsItem
from forex_bot.risk.engine import RiskEngine


class FakeBroker(Broker):
    def __init__(self, positions=None, balance="10000"):
        self._positions = positions or []
        self._balance = balance

    def get_candles(self, instrument, granularity, count):
        raise NotImplementedError

    def get_open_positions(self):
        return self._positions

    def place_order(self, instrument, units, stop_loss=None):
        raise NotImplementedError

    def get_account_summary(self):
        return {"balance": self._balance, "currency": "USD"}


def _settings(**overrides) -> Settings:
    return Settings(_env_file=None, instrument="EUR_USD", **overrides)


def _candle(close: float = 1.10) -> Candle:
    return Candle(timestamp=datetime.now(UTC), open=close, high=close, low=close, close=close, volume=10)


def _decision(action: str = "BUY") -> Decision:
    return Decision(action=action, confidence=3, reason="test")


def test_hold_decision_is_rejected_without_evaluation():
    engine = RiskEngine(_settings())

    verdict = engine.evaluate(_decision("HOLD"), broker=FakeBroker(), candles=[_candle()], news=[])

    assert verdict.approved is False


def test_missing_broker_is_rejected():
    engine = RiskEngine(_settings())

    verdict = engine.evaluate(_decision(), broker=None, candles=[_candle()], news=[])

    assert verdict.approved is False


def test_high_impact_news_in_window_blocks_trade():
    engine = RiskEngine(_settings(risk_news_blackout_minutes=15))
    news = [
        NewsItem(
            timestamp=datetime.now(UTC) + timedelta(minutes=5),
            title="NFP",
            currency="USD",
            impact="high",
            source="test",
        )
    ]

    verdict = engine.evaluate(_decision(), broker=FakeBroker(), candles=[_candle()], news=news)

    assert verdict.approved is False
    assert "Blackout" in verdict.reason


def test_low_impact_news_does_not_block_trade():
    engine = RiskEngine(_settings(risk_news_blackout_minutes=15))
    news = [
        NewsItem(
            timestamp=datetime.now(UTC) + timedelta(minutes=5),
            title="Minor release",
            currency="USD",
            impact="low",
            source="test",
        )
    ]

    verdict = engine.evaluate(_decision(), broker=FakeBroker(), candles=[_candle()], news=news)

    assert verdict.approved is True


def test_existing_open_position_blocks_trade():
    positions = [{"instrument": "EUR_USD", "long": {"units": "100"}, "short": {"units": "0"}}]
    engine = RiskEngine(_settings())

    verdict = engine.evaluate(_decision(), broker=FakeBroker(positions=positions), candles=[_candle()], news=[])

    assert verdict.approved is False
    assert "deja ouverte" in verdict.reason


def test_approved_buy_computes_stop_loss_and_position_size():
    engine = RiskEngine(_settings(risk_stop_loss_pct=0.005, risk_per_trade_pct=0.01))
    broker = FakeBroker(balance="10000")

    verdict = engine.evaluate(_decision("BUY"), broker=broker, candles=[_candle(close=1.10)], news=[])

    assert verdict.approved is True
    assert verdict.stop_loss == pytest.approx(1.0945, rel=1e-6)
    # risk_amount = 10000 * 0.01 = 100 ; stop_distance = 1.10 - 1.0945 = 0.0055
    # position_size = 100 / 0.0055
    assert verdict.position_size == pytest.approx(18181.82, rel=1e-3)


def test_approved_sell_computes_stop_loss_above_entry():
    engine = RiskEngine(_settings(risk_stop_loss_pct=0.005, risk_per_trade_pct=0.01))
    broker = FakeBroker(balance="10000")

    verdict = engine.evaluate(_decision("SELL"), broker=broker, candles=[_candle(close=1.10)], news=[])

    assert verdict.approved is True
    assert verdict.stop_loss == pytest.approx(1.1055, rel=1e-6)
