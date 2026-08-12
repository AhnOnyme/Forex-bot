from forex_bot.brain.prompts import SYSTEM_PROMPT
from forex_bot.config import Settings
from forex_bot.models import Candle, Decision, NewsItem


class QwenBrain:
    """Client du cerveau decisionnel (Qwen via OpenRouter).

    Squelette pour l'instant : la construction/l'envoi de la requete et le
    parsing du JSON seront branches a l'etape 3.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def get_decision(self, candles: list[Candle], news: list[NewsItem]) -> Decision:
        if not self._settings.llm_api_key:
            return Decision(
                action="HOLD",
                confidence=1,
                reason="Brain not yet implemented (LLM_API_KEY absent)",
            )

        # TODO (etape 3): appeler self._settings.llm_base_url (OpenRouter, SDK
        # openai) avec SYSTEM_PROMPT + candles/news, puis valider la reponse
        # JSON avec Decision.model_validate_json(...).
        _ = SYSTEM_PROMPT
        raise NotImplementedError("QwenBrain.get_decision n'est pas encore implemente")
