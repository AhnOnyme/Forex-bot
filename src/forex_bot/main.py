import logging

from forex_bot.config import get_settings
from forex_bot.logging_setup import configure_logging
from forex_bot.pipeline import run_once

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("forex-bot: demarrage du squelette de pipeline (etapes 1-5 en cours de construction)")
    run_once(settings)
    logger.info("forex-bot: cycle termine")


if __name__ == "__main__":
    main()
