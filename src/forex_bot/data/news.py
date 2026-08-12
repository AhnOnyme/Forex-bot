from datetime import UTC, datetime

from forex_bot.models import NewsItem


def fetch_latest_news(currency: str = "USD") -> list[NewsItem]:
    """Recupere les dernieres news/calendrier economique propres.

    TODO (etape 2): brancher sur une source reelle (calendrier economique,
    communiques de banques centrales - source a choisir). En attendant, on
    retourne une news factice pour que le pipeline ait quelque chose a logger.
    """
    return [
        NewsItem(
            timestamp=datetime.now(UTC),
            title="Aucune source de news configuree pour le moment",
            currency=currency,
            impact="low",
            source="stub",
        )
    ]
