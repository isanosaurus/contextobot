# Contextobot

A Discord bot that lets a channel play [Contexto](https://contexto.me/) (the daily word-guessing game) together. Members submit word guesses, the bot scores them against the Contexto API, tracks the closest guesses per channel, renders a leaderboard-style image card, and can hand out AI-generated hints.

## Features

- **Guessing** — send `guess <word>` or `g <word>` in a channel to submit a guess. The bot queries the Contexto API for the word's distance to the answer.
- **Game state per channel** — guesses, game ID, and progress are tracked independently for every channel in [data.json](data.json).
- **Result cards** — after each guess, a PNG leaderboard card showing the closest guesses is rendered ([render_card.py](render_card.py)) and posted back to the channel.
- **Hints** — `!hint` or `!h` asks Gemini for a one-word adjective hint about the day's answer ([hinter.py](hinter.py)), without giving the answer away.
- **Answer scraping** — a background loop scrapes known Contexto answers from an external answers page once an hour ([scrape_contexto.py](scrape_contexto.py)) so hints stay available for past game IDs.
- **`/start`** — slash command to start a new game in the current channel.

## Requirements

- Python 3.12+
- A Discord bot application/token ([Discord Developer Portal](https://discord.com/developers/applications))
- A Google Gemini API key (only needed for `!hint`)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configuring:
   Rename `_config.py` to `config.py` and fill in your Discord bot token and your Gemini API key. (optionally)
   Then edit [config.py](config.py):
   - `TOKEN` — your Discord bot token
   - `GENAI_API_KEY` — your Gemini API key (optional, only needed for hints)
   - `API_BASE` — Contexto API base URL (defaults to the official one, shouldn't need changes)
3. Run the bot:
   ```bash
   python main.py
   ```

## Usage

| Command | Description |
|---|---|
| `/start` | Start a new game in the current channel |
| `guess <word>` / `g <word>` | Submit a word guess |
| `!hint` / `!h` | Get an AI-generated hint for the current game |

## Project structure

- [main.py](main.py) — bot entry point, event handlers, and game-state logic
- [render_card.py](render_card.py) — HTML-to-image rendering of the guess leaderboard card
- [hinter.py](hinter.py) — Gemini-powered hint generation
- [scrape_contexto.py](scrape_contexto.py) — scrapes past Contexto answers for hint lookups from YourDictionary
- [config.py](config.py) — local secrets/config (not shared; see `_config.py` for the template)
- [data.json](data.json) — per-channel game state (guesses, game ID)
- [contexto_answers.json](contexto_answers.json) — cached scraped answers keyed by game ID

## Note

[config.py](config.py) has a live Discord bot token and Gemini API key committed in plain text. Treat both securely.