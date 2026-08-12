from datetime import UTC, datetime, timedelta

from forex_bot.broker.base import Broker
from forex_bot.config import Settings
from forex_bot.models import Candle, Decision, NewsItem, RiskVerdict


class RiskEngine:
    """A le dernier mot sur toute Decision proposee par le brain.

    La decision du LLM n'est qu'un avis : ce moteur applique des regles de
    gestion du risque classiques avant d'autoriser un ordre.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def evaluate(
        self,
        decision: Decision,
        broker: Broker | None,
        candles: list[Candle],
        news: list[NewsItem],
    ) -> RiskVerdict:
        if decision.action == "HOLD":
            return RiskVerdict(approved=False, reason="Decision HOLD, aucun ordre a evaluer")

        if broker is None:
            return RiskVerdict(approved=False, reason="Broker indisponible, impossible de verifier le risque")

        blackout_reason = self._check_news_blackout(news)
        if blackout_reason:
            return RiskVerdict(approved=False, reason=blackout_reason)

        try:
            positions = broker.get_open_positions()
        except Exception as exc:
            return RiskVerdict(approved=False, reason=f"Impossible de verifier les positions ouvertes: {exc}")

        if self._has_open_position(positions, self._settings.instrument):
            return RiskVerdict(approved=False, reason=f"Position deja ouverte sur {self._settings.instrument}")

        if not candles:
            return RiskVerdict(approved=False, reason="Pas de bougie disponible pour calculer le stop-loss")

        entry_price = candles[-1].close
        stop_loss = self._compute_stop_loss(entry_price, decision.action)
        stop_distance = abs(entry_price - stop_loss)

        try:
            account = broker.get_account_summary()
            balance = float(account["balance"])
        except Exception as exc:
            return RiskVerdict(approved=False, reason=f"Impossible de recuperer le solde du compte: {exc}")

        # Money management classique: on ne risque qu'une fraction fixe du
        # solde par trade (risk_per_trade_pct), et la taille de position
        # decoule de la distance du stop-loss - plus le stop est loin, moins
        # on prend d'unites, pour que la perte max reste la meme en valeur.
        risk_amount = balance * self._settings.risk_per_trade_pct
        position_size = risk_amount / stop_distance if stop_distance else 0.0

        return RiskVerdict(
            approved=True,
            reason="Toutes les verifications de risque sont passees",
            stop_loss=round(stop_loss, 5),
            position_size=round(position_size, 2),
        )

    def _compute_stop_loss(self, entry_price: float, action: str) -> float:
        if action == "BUY":
            return entry_price * (1 - self._settings.risk_stop_loss_pct)
        return entry_price * (1 + self._settings.risk_stop_loss_pct)

    def _check_news_blackout(self, news: list[NewsItem]) -> str | None:
        now = datetime.now(UTC)
        window = timedelta(minutes=self._settings.risk_news_blackout_minutes)
        for item in news:
            if item.impact == "high" and abs(item.timestamp - now) <= window:
                return f"Blackout news a fort impact: {item.title} ({item.timestamp.isoformat()})"
        return None

    @staticmethod
    def _has_open_position(positions: list[dict], instrument: str) -> bool:
        for position in positions:
            if position.get("instrument") != instrument:
                continue
            long_units = float(position.get("long", {}).get("units", 0))
            short_units = float(position.get("short", {}).get("units", 0))
            if long_units != 0 or short_units != 0:
                return True
        return False
