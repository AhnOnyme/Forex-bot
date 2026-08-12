from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from forex_bot.models import Candle, Decision, NewsItem, RiskVerdict


def test_decision_accepts_valid_payload():
    decision = Decision(action="BUY", confidence=3, reason="momentum haussier")
    assert decision.action == "BUY"
    assert decision.confidence == 3


def test_decision_rejects_invalid_action():
    with pytest.raises(ValidationError):
        Decision(action="MAYBE", confidence=3, reason="pas clair")


def test_decision_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        Decision(action="HOLD", confidence=9, reason="trop confiant")


def test_candle_accepts_valid_payload():
    candle = Candle(timestamp=datetime.now(UTC), open=1.1, high=1.2, low=1.0, close=1.15, volume=100)
    assert candle.close == 1.15


def test_news_item_rejects_invalid_impact():
    with pytest.raises(ValidationError):
        NewsItem(
            timestamp=datetime.now(UTC),
            title="CPI release",
            currency="USD",
            impact="extreme",
            source="test",
        )


def test_risk_verdict_defaults():
    verdict = RiskVerdict(approved=False, reason="pas encore implemente")
    assert verdict.stop_loss is None
    assert verdict.position_size is None
