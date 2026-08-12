import logging

from forex_bot.brain.qwen_client import QwenBrain
from forex_bot.config import Settings
from forex_bot.data.news import fetch_latest_news
from forex_bot.data.prices import fetch_latest_candles
from forex_bot.notify.telegram import TelegramNotifier
from forex_bot.risk.engine import RiskEngine

logger = logging.getLogger(__name__)


def run_once(settings: Settings) -> None:
    """Un cycle complet : prix -> news -> decision -> risque -> (ordre) -> notification.

    Le broker/risque/brain sont encore des squelettes (etapes 1-4), donc ce
    cycle ne passe jamais d'ordre reel pour l'instant - il prouve juste que
    tous les modules sont bien cables ensemble.
    """
    candles = fetch_latest_candles(settings.instrument)
    logger.info("Prix recuperes: %d bougie(s) pour %s", len(candles), settings.instrument)

    news = fetch_latest_news()
    logger.info("News recuperees: %d item(s)", len(news))

    brain = QwenBrain(settings)
    decision = brain.get_decision(candles, news)
    logger.info("Decision du brain: %s (confiance=%d) - %s", decision.action, decision.confidence, decision.reason)

    risk_engine = RiskEngine()
    verdict = risk_engine.evaluate(decision, broker=None, news=news)
    logger.info("Verdict du risk engine: approved=%s - %s", verdict.approved, verdict.reason)

    if verdict.approved:
        logger.info("Ordre non passe: le broker n'est pas encore implemente (etape 1/2).")
    else:
        logger.info("Aucun ordre passe (verdict refuse ou non implemente).")

    notifier = TelegramNotifier(settings)
    notifier.send(
        f"[forex-bot] {settings.instrument}: decision={decision.action} "
        f"(confiance {decision.confidence}) -> risque approuve={verdict.approved}"
    )
