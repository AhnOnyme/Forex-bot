import logging
from datetime import UTC, datetime

import requests

from forex_bot.config import Settings
from forex_bot.models import NewsItem

logger = logging.getLogger(__name__)

_STUB_NEWS = [
    NewsItem(
        timestamp=datetime.now(UTC),
        title="Aucune source de news disponible pour le moment",
        currency="USD",
        impact="low",
        source="stub",
    )
]

_IMPACT_MAP = {
    "high": "high",
    "medium": "medium",
    "low": "low",
    "holiday": "low",
    "non-economic": "low",
}


def _relevant_currencies(instrument: str) -> set[str]:
    return set(instrument.split("_"))


def _parse_item(raw: dict) -> NewsItem | None:
    try:
        return NewsItem(
            timestamp=datetime.fromisoformat(raw["date"]),
            title=raw["title"],
            currency=raw["country"],
            impact=_IMPACT_MAP.get(str(raw.get("impact", "")).strip().lower(), "low"),
            source="forexfactory",
        )
    except (KeyError, ValueError) as exc:
        logger.warning("Item de calendrier ignore (format inattendu): %s", exc)
        return None


def fetch_latest_news(settings: Settings) -> list[NewsItem]:
    """Recupere le calendrier economique ForexFactory, filtre sur les devises
    de l'instrument trade (pour reduire le bruit).

    Retombe sur une news factice en cas d'erreur reseau/format, comme le
    reste du pipeline. Une liste vide (sans erreur) signifie simplement
    qu'aucune news pertinente n'est prevue pour l'instant.
    """
    try:
        response = requests.get(settings.news_calendar_url, timeout=10)
        response.raise_for_status()
        raw_items = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Echec de recuperation du calendrier economique (%s), fallback stub", exc)
        return _STUB_NEWS

    relevant = _relevant_currencies(settings.instrument)
    items = [item for raw in raw_items if (item := _parse_item(raw)) is not None]
    filtered = [item for item in items if item.currency in relevant]

    if not filtered:
        logger.info("Aucune news pertinente pour %s dans le calendrier recupere", settings.instrument)

    return filtered
