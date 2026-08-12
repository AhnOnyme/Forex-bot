import logging

from forex_bot.config import get_settings
from forex_bot.logging_setup import configure_logging
from forex_bot.pipeline import run_forever, run_once

logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    if settings.run_once_only:
        logger.info("forex-bot: cycle unique (RUN_ONCE_ONLY=true)")
        run_once(settings)
        logger.info("forex-bot: cycle termine")
        return

    logger.info("forex-bot: demarrage en boucle continue")
    run_forever(settings)


if __name__ == "__main__":
    main()
