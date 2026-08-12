from datetime import UTC, datetime

from forex_bot.models import Candle


def fetch_latest_candles(instrument: str, count: int = 10) -> list[Candle]:
    """Recupere les dernieres bougies OHLCV pour un instrument.

    TODO (etape 2): brancher sur OandaBroker.get_candles. En attendant, on
    retourne une bougie factice pour que le pipeline ait quelque chose a logger.
    """
    return [
        Candle(
            timestamp=datetime.now(UTC),
            open=1.0,
            high=1.0,
            low=1.0,
            close=1.0,
            volume=0,
        )
    ]
