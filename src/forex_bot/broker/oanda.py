from typing import Any

from forex_bot.broker.base import Broker
from forex_bot.config import Settings
from forex_bot.models import Candle


class OandaBroker(Broker):
    """Broker OANDA (v20 REST API) via oandapyV20.

    Squelette pour l'instant : les appels HTTP reels seront branches a l'etape 2.
    Le garde-fou practice/live vit ici, au plus pres du seul endroit qui parle
    reellement au compte OANDA.
    """

    def __init__(self, settings: Settings):
        if settings.oanda_environment != "practice":
            raise RuntimeError(
                "OandaBroker refuse de demarrer hors de l'environnement 'practice' "
                "sans confirmation explicite supplementaire."
            )
        self._settings = settings

    def get_candles(self, instrument: str, granularity: str, count: int) -> list[Candle]:
        # TODO (etape 2): appeler l'endpoint /instruments/{instrument}/candles via oandapyV20.
        raise NotImplementedError("OandaBroker.get_candles n'est pas encore implemente")

    def get_open_positions(self) -> list[dict[str, Any]]:
        # TODO (etape 4): appeler l'endpoint /accounts/{accountID}/openPositions.
        raise NotImplementedError("OandaBroker.get_open_positions n'est pas encore implemente")

    def place_order(self, instrument: str, units: float, stop_loss: float | None = None) -> dict[str, Any]:
        # TODO (etape 4): appeler l'endpoint /accounts/{accountID}/orders.
        raise NotImplementedError("OandaBroker.place_order n'est pas encore implemente")

    def get_account_summary(self) -> dict[str, Any]:
        # TODO (etape 1): appeler l'endpoint /accounts/{accountID}/summary.
        raise NotImplementedError("OandaBroker.get_account_summary n'est pas encore implemente")
