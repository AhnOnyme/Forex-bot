import re
from datetime import datetime
from typing import Any

import oandapyV20
from oandapyV20.endpoints.accounts import AccountSummary
from oandapyV20.endpoints.instruments import InstrumentsCandles
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.endpoints.positions import OpenPositions
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
        request = OpenPositions(accountID=self._settings.oanda_account_id)
        try:
            self._client.request(request)
        except V20Error as exc:
            raise RuntimeError(f"Echec de recuperation des positions ouvertes OANDA: {exc}") from exc
        return request.response.get("positions", [])

    def place_order(self, instrument: str, units: float, stop_loss: float | None = None) -> dict[str, Any]:
        # Convention OANDA : units positif = achat, negatif = vente. C'est a
        # l'appelant (risk engine / pipeline) d'appliquer le signe selon BUY/SELL.
        order: dict[str, Any] = {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(int(units)),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
        }
        if stop_loss is not None:
            order["stopLossOnFill"] = {"price": f"{stop_loss:.5f}"}

        request = OrderCreate(accountID=self._settings.oanda_account_id, data={"order": order})
        try:
            self._client.request(request)
        except V20Error as exc:
            raise RuntimeError(f"Echec du passage d'ordre OANDA pour {instrument}: {exc}") from exc
        return request.response

    def get_account_summary(self) -> dict[str, Any]:
        request = AccountSummary(accountID=self._settings.oanda_account_id)
        try:
            self._client.request(request)
        except V20Error as exc:
            raise RuntimeError(f"Echec de recuperation du resume de compte OANDA: {exc}") from exc
        return request.response.get("account", {})
