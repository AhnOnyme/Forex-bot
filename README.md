# Forex-bot

Agent de trading forex autonome : pipeline decisionnel news + prix -> LLM (Qwen) -> moteur de risque -> execution.

> ⚠️ **Ce bot ne trade que sur un compte OANDA practice (demo, argent virtuel).**
> Le passage en compte reel (`live`) n'est pas implemente et ne le sera qu'apres
> validation explicite du garde-fou de securite dans `src/forex_bot/config.py` /
> `src/forex_bot/broker/oanda.py`.

## Roadmap en 5 etapes

1. ✅ **Paper trading** — connexion a un compte OANDA practice, aucune perte possible.
2. ✅ **Pipeline de donnees** — recuperation des bougies OHLCV (OANDA) et des news/calendrier
   economique (flux ForexFactory, filtre sur les devises de l'instrument trade).
3. ✅ **Le "cerveau"** — Qwen (via OpenRouter, SDK `openai`) analyse les donnees et repond en
   JSON strict : `{"action": "BUY"|"SELL"|"HOLD", "confidence": 1-5, "reason": "..."}`. Fallback
   `HOLD` sur toute reponse non exploitable (pas de cle, erreur API, JSON invalide).
4. ✅ **Moteur de risque** — la decision du LLM n'est qu'un avis ; `RiskEngine` verifie position
   deja ouverte, blackout news a fort impact, calcule stop-loss et taille de position (risque
   fixe % du solde), puis **passe reellement l'ordre sur le compte practice** si tout est vert.
5. ⬜ **Automatisation & monitoring** — boucle de scheduling continue, deploiement VPS,
   durcissement du Dockerfile/compose.

Ce depot contient un pipeline complet et fonctionnel de bout en bout, avec des implementations
de secours sures partout ou une dependance externe (OANDA, OpenRouter, Telegram, calendrier)
est absente ou indisponible — voir la section "Robustesse" ci-dessous.

## Robustesse (comportement de secours)

Chaque etage du pipeline peut fonctionner meme si sa dependance externe n'est pas configuree
ou est temporairement indisponible, plutot que de faire planter le cycle :

| Etage | Sans configuration / en cas d'erreur |
|---|---|
| Prix (OANDA) | Bougie factice, warning logue |
| News (ForexFactory) | News factice, warning logue |
| Cerveau (Qwen) | Decision `HOLD`, raison expliquee |
| Risque | Refuse l'ordre (jamais d'approbation par defaut) |
| Telegram | Message juste logue, pas envoye |

## Gestion du risque (etape 4) — comment ca marche

Quand le brain propose `BUY` ou `SELL`, `RiskEngine` (dans `src/forex_bot/risk/engine.py`)
verifie dans l'ordre :
1. Pas de news a fort impact dans les `RISK_NEWS_BLACKOUT_MINUTES` minutes (defaut 15).
2. Pas de position deja ouverte sur l'instrument.
3. Calcule un stop-loss a `RISK_STOP_LOSS_PCT` (defaut 0.5%) du prix d'entree.
4. Calcule la taille de position : `(solde du compte * RISK_PER_TRADE_PCT) / distance du stop-loss`
   — une regle de money management classique : on ne risque qu'un pourcentage fixe du solde
   par trade, quelle que soit la distance du stop.

Si tout passe, l'ordre est reellement envoye sur le compte practice OANDA avec le stop-loss
attache. Ces 3 parametres sont ajustables dans `.env`.

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
juste loggee) — voir la section "Robustesse" plus haut.

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
