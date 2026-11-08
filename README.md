# Glenride Telegram Romance Simulation Bot

## Overview
Interactive fiction Telegram bot set in a futuristic neon city where players balance love, temptation, and career choices through inline keyboards.

## Tech Stack & Patterns
- **Language:** Python 3.13+
- **Framework:** `python-telegram-bot` for update handling
- **State & Validation:** Custom persistence layer with `pydantic` models
- **HTTP Utilities:** `httpx` for outbound calls (payments, analytics)
- **Testing:** `pytest` + `pytest-asyncio`
- **Linting/Formatting:** `ruff`
- **Packaging:** PEP 621 (`pyproject.toml`) with editable installs
- **Content Storage:** JSON scene files under `content/scenes/`
- **Configuration:** Environment-specific settings + optional banned-word list in `config/`

## Repo Structure
```
bot/                  # Application modules
  handlers/           # Command & callback handlers (start, profile, scene)
  scenes/             # Scene engine (models, loader, renderer)
  onboarding/         # Name/pronoun validation & sanitization
  state.py            # User state persistence (SQLite)
  config.py           # Environment configuration
  main.py             # Bot entry point
content/scenes/       # Authored narrative JSON data
  chapter_tutorial.json  # Tutorial scenes (12 scenes)
  chapter_1.json         # "Neon Nights & Notifications" (30 scenes)
config/               # Supplemental config assets (e.g., banned words)
tests/                # Automated test suites
pyproject.toml        # Project metadata & dependencies
README.md             # Patterns & stack reference
```

## Scene Engine Architecture

### Scene JSON Format
Scenes are stored in `content/scenes/{chapter_id}.json` with localization support:

```json
{
  "chapter_id": "chapter_tutorial",
  "scenes": [
    {
      "id": "chapter_tutorial_intro",
      "narrative": {"en": "Welcome, {player_name}!"},
      "choices": [
        {
          "id": "choice_1",
          "text": {"en": "Continue"},
          "next_scene_id": "next_scene",
          "effects": {"love_integrity": 5},
          "emoji": "❤️"
        }
      ],
      "set_flags": {"tutorial_started": true}
    }
  ]
}
```

### Key Models
- **Scene:** Narrative text, choices, stat effects, flags
- **Choice:** Button text, destination scene, conditions, effects
- **SceneCondition:** Stat requirements, flags, premium checks
- **StatEffect:** Stat deltas applied on choice selection

### Stats System
- ❤️ **Love Integrity:** Commitment to genuine connections
- 🔥 **Temptation:** How much you've given in to shortcuts
- 💼 **Career Status:** Professional standing
- ⚡ **Energy:** Capacity for activities (regenerates over time)

## Running the Bot

```bash
# Install dependencies
pip install -e .

# Set environment variables (or create .env file)
export BOT_TOKEN=your_telegram_bot_token
export APP_ENV=dev

# Run the bot
python -m bot.main
```

## Running Tests

```bash
pytest tests/ -v
```
