import logging

from forex_bot.brain.qwen_client import QwenBrain
from forex_bot.broker.base import Broker
from forex_bot.broker.oanda import OandaBroker
from forex_bot.config import Settings
from forex_bot.data.news import fetch_latest_news
from forex_bot.data.prices import fetch_latest_candles
from forex_bot.notify.telegram import TelegramNotifier
from forex_bot.risk.engine import RiskEngine

logger = logging.getLogger(__name__)


def _build_broker(settings: Settings) -> Broker | None:
    if not settings.oanda_api_key or not settings.oanda_account_id:
        logger.warning("Credentials OANDA absents, le broker n'est pas disponible (mode stub).")
        return None
    try:
        broker = OandaBroker(settings)
        account = broker.get_account_summary()
        logger.info(
            "Connexion OANDA OK: solde=%s %s",
            account.get("balance"),
            account.get("currency"),
        )
        return broker
    except Exception:
        logger.exception("Impossible de se connecter a OANDA, retour au mode stub.")
        return None


def run_once(settings: Settings) -> None:
    """Un cycle complet : prix -> news -> decision -> risque -> (ordre) -> notification.

    Le risque/brain sont encore des squelettes (etapes 3-4), donc ce cycle ne
    passe jamais d'ordre reel pour l'instant.
    """
    broker = _build_broker(settings)

    candles = fetch_latest_candles(broker, settings.instrument, settings.oanda_granularity, settings.oanda_candle_count)
    logger.info("Prix recuperes: %d bougie(s) pour %s", len(candles), settings.instrument)

    news = fetch_latest_news(settings)
    logger.info("News recuperees: %d item(s)", len(news))

    brain = QwenBrain(settings)
    decision = brain.get_decision(candles, news)
    logger.info("Decision du brain: %s (confiance=%d) - %s", decision.action, decision.confidence, decision.reason)

    risk_engine = RiskEngine()
    verdict = risk_engine.evaluate(decision, broker=broker, news=news)
    logger.info("Verdict du risk engine: approved=%s - %s", verdict.approved, verdict.reason)

    if verdict.approved:
        logger.info("Ordre non passe: le passage d'ordre n'est pas encore implemente (etape 4).")
    else:
        logger.info("Aucun ordre passe (verdict refuse ou non implemente).")

    notifier = TelegramNotifier(settings)
    notifier.send(
        f"[forex-bot] {settings.instrument}: decision={decision.action} "
        f"(confiance {decision.confidence}) -> risque approuve={verdict.approved}"
    )
