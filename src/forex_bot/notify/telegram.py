import logging

import requests

from forex_bot.config import Settings

logger = logging.getLogger(__name__)

_TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramNotifier:
    """Envoie des messages sortants via l'API Bot Telegram.

    No-op (avec juste un log) si le token/chat id ne sont pas configures,
    pour que le pipeline tourne meme sans bot Telegram configure.
    """

    def __init__(self, settings: Settings):
        self._token = settings.telegram_bot_token
        self._chat_id = settings.telegram_chat_id

    def send(self, message: str) -> None:
        if not self._token or not self._chat_id:
            logger.info("Telegram non configure, message non envoye: %s", message)
            return

        url = f"{_TELEGRAM_API_BASE}/bot{self._token}/sendMessage"
        response = requests.post(
            url,
            json={"chat_id": self._chat_id, "text": message},
            timeout=10,
        )
        response.raise_for_status()
