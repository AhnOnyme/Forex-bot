import re
from datetime import datetime
from typing import Any

import oandapyV20
from oandapyV20.endpoints.accounts import AccountSummary
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.exceptions import V20Error

from forex_bot.broker.base import Broker
from forex_bot.config import Settings
from forex_bot.models import Candle


def _parse_oanda_time(value: str) -> datetime:
    """OANDA renvoie des timestamps avec 9 chiffres de fraction de seconde
    (nanosecondes) - `datetime.fromisoformat` n'en accepte que 6 (microsecondes).
    """
    value = re.sub(r"(\.\d{6})\d*Z$", r"\1+00:00", value)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class OandaBroker(Broker):
    """Broker OANDA (v20 REST API) via oandapyV20.

    Le garde-fou practice/live vit ici, au plus pres du seul endroit qui parle
    reellement au compte OANDA.
    """

    def __init__(self, settings: Settings, api_client: oandapyV20.API | None = None):
        if settings.oanda_environment != "practice":
            raise RuntimeError(
                "OandaBroker refuse de demarrer hors de l'environnement 'practice' "
                "sans confirmation explicite supplementaire."
            )
        self._settings = settings
        self._client = api_client or oandapyV20.API(
            access_token=settings.oanda_api_key, environment=settings.oanda_environment
        )

    def get_candles(self, instrument: str, granularity: str, count: int) -> list[Candle]:
        request = InstrumentsCandles(
            instrument=instrument,
            params={"count": count, "granularity": granularity, "price": "M"},
        )
        try:
            self._client.request(request)
        except V20Error as exc:
            raise RuntimeError(f"Echec de recuperation des bougies OANDA pour {instrument}: {exc}") from exc

        candles = []
        for item in request.response.get("candles", []):
            mid = item["mid"]
            candles.append(
                Candle(
                    timestamp=_parse_oanda_time(item["time"]),
                    open=float(mid["o"]),
                    high=float(mid["h"]),
                    low=float(mid["l"]),
                    close=float(mid["c"]),
                    volume=int(item["volume"]),
                )
            )
        return candles

    def get_open_positions(self) -> list[dict[str, Any]]:
        # TODO (etape 4): appeler l'endpoint /accounts/{accountID}/openPositions.
        raise NotImplementedError("OandaBroker.get_open_positions n'est pas encore implemente")

    def place_order(self, instrument: str, units: float, stop_loss: float | None = None) -> dict[str, Any]:
        # TODO (etape 4): appeler l'endpoint /accounts/{accountID}/orders.
        raise NotImplementedError("OandaBroker.place_order n'est pas encore implemente")

    def get_account_summary(self) -> dict[str, Any]:
        request = AccountSummary(accountID=self._settings.oanda_account_id)
        try:
            self._client.request(request)
        except V20Error as exc:
            raise RuntimeError(f"Echec de recuperation du resume de compte OANDA: {exc}") from exc
        return request.response.get("account", {})
