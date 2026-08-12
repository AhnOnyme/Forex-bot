from abc import ABC, abstractmethod
from typing import Any

from forex_bot.models import Candle


class Broker(ABC):
    """Interface commune a tout broker (OANDA practice/live, ou un autre plus tard)."""

    @abstractmethod
    def get_candles(self, instrument: str, granularity: str, count: int) -> list[Candle]:
        ...

    @abstractmethod
    def get_open_positions(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def place_order(self, instrument: str, units: float, stop_loss: float | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_account_summary(self) -> dict[str, Any]:
        ...
