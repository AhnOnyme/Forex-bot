import json
import logging
import re

from openai import OpenAI

from forex_bot.brain.prompts import SYSTEM_PROMPT
from forex_bot.config import Settings
from forex_bot.models import Candle, Decision, NewsItem

logger = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _format_market_data(candles: list[Candle], news: list[NewsItem], instrument: str, candle_window: int) -> str:
    lines = [f"Instrument: {instrument}", "", "Bougies recentes (OHLCV):"]
    for candle in candles[-candle_window:]:
        lines.append(
            f"{candle.timestamp.isoformat()} O={candle.open} H={candle.high} "
            f"L={candle.low} C={candle.close} V={candle.volume}"
        )

    lines.append("")
    lines.append("News/evenements macro pertinents:")
    if news:
        for item in news:
            lines.append(f"[{item.currency}][{item.impact}] {item.title} ({item.timestamp.isoformat()})")
    else:
        lines.append("Aucune news pertinente pour le moment.")

    return "\n".join(lines)


class QwenBrain:
    """Client du cerveau decisionnel (Qwen via OpenRouter, SDK openai avec base_url custom)."""

    def __init__(self, settings: Settings, client: OpenAI | None = None):
        self._settings = settings
        self._client = client

    def get_decision(self, candles: list[Candle], news: list[NewsItem]) -> Decision:
        if not self._settings.llm_api_key:
            return Decision(
                action="HOLD",
                confidence=1,
                reason="Brain not yet implemented (LLM_API_KEY absent)",
            )

        client = self._client or OpenAI(api_key=self._settings.llm_api_key, base_url=self._settings.llm_base_url)
        market_data = _format_market_data(
            candles, news, self._settings.instrument, self._settings.llm_candle_window
        )

        # Le prompt systeme impose deja un JSON strict, mais un LLM peut toujours
        # devier (texte autour du JSON, action hors enum...) : on ne fait jamais
        # confiance aveuglement, on parse/valide, et on retombe sur HOLD sinon -
        # meme philosophie de robustesse que le reste du pipeline (prix/news/telegram).
        try:
            response = client.chat.completions.create(
                model=self._settings.llm_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": market_data},
                ],
            )
            content = response.choices[0].message.content or ""
            return self._parse_decision(content)
        except Exception as exc:
            logger.warning("Echec de la decision Qwen (%s), fallback HOLD", exc)
            return Decision(action="HOLD", confidence=1, reason=f"Erreur brain: {exc}")

    @staticmethod
    def _parse_decision(content: str) -> Decision:
        match = _JSON_BLOCK_RE.search(content)
        if not match:
            raise ValueError(f"Aucun JSON trouve dans la reponse du LLM: {content!r}")
        payload = json.loads(match.group(0))
        return Decision.model_validate(payload)
