import logging

from forex_bot.brain.qwen_client import QwenBrain
from forex_bot.broker.base import Broker
from forex_bot.broker.oanda import OandaBroker
from forex_bot.config import Settings
from forex_bot.data.news import fetch_latest_news
from forex_bot.data.prices import fetch_latest_candles
from forex_bot.models import Decision, RiskVerdict
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


def _place_order(broker: Broker, settings: Settings, decision: Decision, verdict: RiskVerdict) -> str:
    # Convention OANDA: units positif = achat, negatif = vente.
    units = verdict.position_size if decision.action == "BUY" else -verdict.position_size
    try:
        result = broker.place_order(settings.instrument, units, stop_loss=verdict.stop_loss)
        logger.info("Ordre passe sur %s: units=%s stop_loss=%s -> %s", settings.instrument, units, verdict.stop_loss, result)
        return "ordre passe"
    except Exception:
        logger.exception("Echec du passage d'ordre sur %s", settings.instrument)
        return "echec du passage d'ordre"


def run_once(settings: Settings) -> None:
    """Un cycle complet : prix -> news -> decision -> risque -> (ordre) -> notification."""
    broker = _build_broker(settings)

    candles = fetch_latest_candles(broker, settings.instrument, settings.oanda_granularity, settings.oanda_candle_count)
    logger.info("Prix recuperes: %d bougie(s) pour %s", len(candles), settings.instrument)

    news = fetch_latest_news(settings)
    logger.info("News recuperees: %d item(s)", len(news))

    brain = QwenBrain(settings)
    decision = brain.get_decision(candles, news)
    logger.info("Decision du brain: %s (confiance=%d) - %s", decision.action, decision.confidence, decision.reason)

    risk_engine = RiskEngine(settings)
    verdict = risk_engine.evaluate(decision, broker=broker, candles=candles, news=news)
    logger.info("Verdict du risk engine: approved=%s - %s", verdict.approved, verdict.reason)

    if verdict.approved and broker is not None:
        order_status = _place_order(broker, settings, decision, verdict)
    else:
        order_status = "aucun ordre passe"
        logger.info("Aucun ordre passe (%s)", verdict.reason)

    notifier = TelegramNotifier(settings)
    notifier.send(
        f"[forex-bot] {settings.instrument}: decision={decision.action} "
        f"(confiance {decision.confidence}) -> risque approuve={verdict.approved} -> {order_status}"
    )
