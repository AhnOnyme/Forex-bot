from datetime import UTC, datetime

from forex_bot.brain.qwen_client import QwenBrain
from forex_bot.config import Settings
from forex_bot.models import Candle, NewsItem


def _settings(**overrides) -> Settings:
    overrides.setdefault("llm_api_key", "key")
    return Settings(_env_file=None, **overrides)


def _candles():
    return [Candle(timestamp=datetime.now(UTC), open=1.1, high=1.2, low=1.0, close=1.15, volume=100)]


def _news():
    return [NewsItem(timestamp=datetime.now(UTC), title="CPI", currency="USD", impact="high", source="test")]


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeChatResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, content=None, raise_error=False):
        self._content = content
        self._raise_error = raise_error

    def create(self, **kwargs):
        if self._raise_error:
            raise RuntimeError("boom")
        return FakeChatResponse(self._content)


class FakeChat:
    def __init__(self, completions):
        self.completions = completions


class FakeOpenAIClient:
    def __init__(self, content=None, raise_error=False):
        self.chat = FakeChat(FakeCompletions(content=content, raise_error=raise_error))


def test_get_decision_parses_valid_json():
    client = FakeOpenAIClient(content='{"action": "BUY", "confidence": 4, "reason": "momentum haussier"}')
    brain = QwenBrain(_settings(), client=client)

    decision = brain.get_decision(_candles(), _news())

    assert decision.action == "BUY"
    assert decision.confidence == 4


def test_get_decision_falls_back_to_hold_on_unparsable_response():
    client = FakeOpenAIClient(content="Je pense que ca va monter mais je ne suis pas sur.")
    brain = QwenBrain(_settings(), client=client)

    decision = brain.get_decision(_candles(), _news())

    assert decision.action == "HOLD"


def test_get_decision_falls_back_to_hold_on_api_error():
    client = FakeOpenAIClient(raise_error=True)
    brain = QwenBrain(_settings(), client=client)

    decision = brain.get_decision(_candles(), _news())

    assert decision.action == "HOLD"


def test_get_decision_without_api_key_skips_the_call():
    brain = QwenBrain(_settings(llm_api_key=None), client=None)

    decision = brain.get_decision(_candles(), _news())

    assert decision.action == "HOLD"
    assert "LLM_API_KEY" in decision.reason
