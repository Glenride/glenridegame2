# Task List: Telegram Romance Simulation Game Bot (derived from PRD)

## Relevant Files

- `bot/main.py` – Bot entry point, update handlers, command registration, and polling/webhook configuration.
- `bot/state.py` – Persistence helpers for user stats, chapters, flags, and energy.
- `bot/scenes.py` – Structured scene definitions plus helpers for scene lookup and choice metadata.
- `bot/handlers.py` – `/start`, `/profile`, and callback query logic that connects updates to the scene engine.
- `bot/payments.py` – Telegram Payments integration, entitlement checks, and premium pack storage.
- `bot/retention.py` – Daily login rewards, weekly event toggles, and broadcast hooks.
- `bot/analytics.py` – Event logging helpers for funnels and optional Amplitude/Mixpanel forwarding.
- `content/scenes/*.json` – Authored narrative content (tutorial, Chapter 1, premium route) with localization-ready structure.
- `config/banned_words.txt` – Optional profanity/slur list to sanitize player-provided names.
- `tests/test_handlers.py` – Behavioral tests for onboarding and choice handling flows.
- `tests/test_state.py` – Unit tests for state persistence, energy rules, and stat calculations.
- `tests/test_analytics.py` – Ensures required events are emitted with correct payloads.

### Notes

- Keep implementation aligned with existing patterns; place unit tests beside the modules they cover when practical.
- Run the full automated test suite before marking any parent task complete.

## Tasks

- [x] 1.0 Establish bot infrastructure (commit: 410126c)
  - [x] 1.1 Scaffold Python project with dependency management, linting, and `python-telegram-bot` (or `aiogram`).
  - [x] 1.2 Configure environment separation (dev/test/prod) for tokens, DB URLs, and payment keys.
  - [x] 1.3 Implement `/start` and `/profile` command handlers that delegate to placeholder logic.
  - [x] 1.4 Add structured logging/metrics to capture update latency and errors.
  - [x] 1.5 Build name/pronoun onboarding flow with sanitization (2–20 chars, strip markup, banned-word filter, fixed pronoun list).
- [x] 2.0 Implement persistent state management (commit: 449fcb4)
  - [x] 2.1 Define database schema (or Redis structures) for user stats, chapter progress, flags, and premium packs.
  - [x] 2.2 Build `load_user_state`, `save_user_state`, and atomic stat update helpers with concurrency safeguards.
  - [x] 2.3 Cover state transitions, energy depletion/regeneration, and pronoun/name storage with automated tests.
  - [x] 2.4 Store premium entitlements, daily login streaks, and analytics opt-in flags per user.
- [ ] 3.0 Build scene engine and initial content
  - [ ] 3.1 Encode tutorial (8–12 scenes) plus “Neon Nights & Notifications” chapter (20–30 scenes) with stat effects and branching metadata.
  - [ ] 3.2 Implement renderer that outputs narrative text, stat summaries, and inline keyboards (including disabled/locked options).
  - [ ] 3.3 Wire callback handling to validate choices, apply effects, transition scenes, and emit analytics events for every scene/choice.
  - [ ] 3.4 Structure scene data to keep text separate from business logic for future localization.
- [ ] 4.0 Add monetization and energy systems
  - [ ] 4.1 Integrate Telegram Payments API using a supported provider (e.g., Stripe) with USD pricing at launch.
  - [ ] 4.2 Add metadata to support EUR plus one configurable local currency; surface price selection per environment.
  - [ ] 4.3 Gate premium scenes/choices based on entitlements and provide upsell flows when unavailable.
  - [ ] 4.4 Implement configurable energy regeneration timers plus purchasable refills and log paywall/purchase funnel events.
- [ ] 5.0 Implement retention and broadcast mechanics
  - [ ] 5.1 Track daily logins, award configurable bonuses, and expose status to players.
  - [ ] 5.2 Add weekly event/season flag toggles to unlock limited scenes.
  - [ ] 5.3 Provide admin/bot command to broadcast announcements to linked Telegram channel.
- [ ] 6.0 Implement analytics and telemetry pipeline
  - [ ] 6.1 Create `analytics_events` schema (user_id, timestamp, event_type, properties JSON) and server-side logger.
  - [ ] 6.2 Emit required funnel events (`start_game`, `tutorial_complete`, `chapter_complete`, `premium_paywall_shown`, `purchase_initiated`, `purchase_success`, `scene_view`, `choice_made`).
  - [ ] 6.3 Add optional Amplitude/Mixpanel dispatchers with environment-based toggles and retry policies.
- [ ] 7.0 Deliver premium content scope
  - [ ] 7.1 Author first premium romance route with ≥30 scenes, ≥5 premium-only decision points, and ≥2 endings.
  - [ ] 7.2 Instrument premium scenes with analytics and entitlement metadata.