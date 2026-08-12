FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

# Ne pas tourner en root dans le conteneur - reduit l'impact d'une eventuelle
# faille dans une dependance.
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 1000 forexbot
USER forexbot

CMD ["python", "-m", "forex_bot.main"]
