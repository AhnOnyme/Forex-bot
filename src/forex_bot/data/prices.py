import logging
from datetime import UTC, datetime

from forex_bot.broker.base import Broker
from forex_bot.models import Candle

logger = logging.getLogger(__name__)

_STUB_CANDLE = [
    Candle(
        timestamp=datetime.now(UTC),
        open=1.0,
        high=1.0,
        low=1.0,
        close=1.0,
        volume=0,
    )
]


def fetch_latest_candles(broker: Broker | None, instrument: str, granularity: str, count: int) -> list[Candle]:
    """Recupere les dernieres bougies OHLCV pour un instrument via le broker.

    Si aucun broker n'est disponible (credentials OANDA absents/invalides),
    retombe sur une bougie factice pour que le pipeline ait quand meme
    quelque chose a logger.
    """
    if broker is None:
        logger.warning("Aucun broker disponible, retour d'une bougie factice pour %s", instrument)
        return _STUB_CANDLE

    return broker.get_candles(instrument, granularity, count)
