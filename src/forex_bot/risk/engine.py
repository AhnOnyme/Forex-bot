from forex_bot.broker.base import Broker
from forex_bot.models import Decision, NewsItem, RiskVerdict


class RiskEngine:
    """A le dernier mot sur toute Decision proposee par le brain.

    TODO (etape 4): implementer les vrais controles :
    - position deja ouverte sur l'instrument ?
    - stop-loss calcule et coherent ?
    - blackout : grosse annonce macro dans les minutes qui viennent ?
    Par securite, ce squelette refuse systematiquement tant qu'il n'est pas implemente.
    """

    def evaluate(self, decision: Decision, broker: Broker | None, news: list[NewsItem]) -> RiskVerdict:
        return RiskVerdict(approved=False, reason="risk engine not yet implemented")
