# Forex-bot

Agent de trading forex autonome : pipeline decisionnel news + prix -> LLM (Qwen) -> moteur de risque -> execution.

> ⚠️ **Ce bot ne trade que sur un compte OANDA practice (demo, argent virtuel).**
> Le passage en compte reel (`live`) n'est pas implemente et ne le sera qu'apres
> validation explicite du garde-fou de securite dans `src/forex_bot/config.py` /
> `src/forex_bot/broker/oanda.py`.

## Roadmap en 5 etapes

1. **Paper trading** — connexion a un compte OANDA practice, aucune perte possible.
2. **Pipeline de donnees** — recuperation des bougies OHLCV (OANDA) et des news/calendrier
   economique propres (source institutionnelle, pas de flux social bruyant).
3. **Le "cerveau"** — un modele open-weight (Qwen, via OpenRouter) analyse les donnees et
   repond en JSON strict : `{"action": "BUY"|"SELL"|"HOLD", "confidence": 1-5, "reason": "..."}`.
4. **Moteur de risque** — la decision du LLM n'est qu'un avis ; un moteur Python verifie
   positions ouvertes, stop-loss, blackout news avant de valider un ordre simule.
5. **Automatisation & monitoring** — deploiement Docker sur un VPS, notifications Telegram
   a chaque decision prise.

Ce depot contient pour l'instant le **squelette du projet** (structure, contrats de donnees,
pipeline cable de bout en bout avec des implementations de secours sures). Les etapes 1 a 5
seront remplies progressivement dans les fichiers correspondants (voir les `TODO` dans le code).

## Structure du projet

```
src/forex_bot/
├── main.py            # point d'entree
├── config.py           # variables d'environnement / parametres
├── pipeline.py          # orchestrateur du cycle prix -> news -> decision -> risque -> notif
├── models.py            # contrats de donnees partages (Candle, NewsItem, Decision, RiskVerdict)
├── broker/               # interface + implementation OANDA
├── data/                  # recuperation prix / news
├── brain/                  # client LLM (Qwen via OpenRouter) + prompt systeme
├── risk/                    # moteur de risque
└── notify/                   # notifications Telegram
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# renseigner .env avec tes cles (OANDA, OpenRouter, Telegram) - optionnel pour le squelette
```

## Lancer le bot

```bash
python -m forex_bot.main
```

Sans aucune cle API configuree, le pipeline tourne quand meme de bout en bout avec des
implementations de secours (decision `HOLD` par defaut, aucun ordre passe, notification
juste loggee) — c'est le comportement attendu tant que les etapes 1 a 5 ne sont pas
completement implementees.

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t forex-bot .
docker run --env-file .env forex-bot
# ou
docker compose up --build
```
