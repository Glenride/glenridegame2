# PRD: Telegram Romance Simulation Game Bot

## 1. Introduction / Overview

A Telegram chat-based simulation game set in a futuristic neon city where players search for genuine love while balancing career ambitions and constant temptations. The bot delivers interactive fiction through narrative messages and inline keyboard choices, maintaining persistent player state, stats, and branching storylines. The goal of the initial release is to ship a compelling tutorial plus one core chapter with monetizable premium routes.

## 2. Goals

1. Deliver a stateful interactive fiction experience that reacts to player choices within 1–2 seconds.
2. Provide clear stat feedback (love integrity, temptation, career status, energy) to emphasize player agency.
3. Introduce monetization hooks (premium routes/choices, optional energy refills) without blocking core progression.
4. Support safe persistence of player state across sessions for at least 10k daily active users.
5. Lay groundwork for seasonal events, achievements, and future chapters.

## 3. User Stories

1. **Romance gamer**: “As a romance-focused player, I want nuanced love interest scenes so I can roleplay meaningful relationships.”
2. **Sci-fi fan**: “As a cyberpunk enthusiast, I want moral dilemmas involving AI temptations so I can explore futuristic ethics.”
3. **Telegram native**: “As a Telegram-first user, I want to play entirely inside chat so I can avoid installing another app.”
4. **Paying user**: “As a dedicated player, I want optional premium routes or boosts so I can unlock richer scenes quickly.”
5. **Returning player**: “As someone who drops in daily, I want bonuses and reminders so I feel rewarded for consistent play.”

## 4. Functional Requirements

1. **Onboarding**
   1.1 Bot must respond to `/start` by creating or loading user state and presenting the intro scene.
   1.2 Collect player name and pronoun preference via quick replies before the first meaningful choice.
   1.3 Sanitize player-provided names (strip markup, enforce 2–20 characters, ban obvious slurs) and offer a fixed set of pronoun quick-picks (she/her, he/him, they/them) to limit abuse.

2. **Scene Engine**
   2.1 Store scenes with IDs, narrative text, 2–4 choices, stat effects, next-scene IDs, and optional premium requirements.
   2.2 Render inline keyboard buttons with unique callback data per choice; premium options must be visually distinct and validated.
   2.3 Support conditional choices (e.g., requires love_integrity > 50) and fallback text when unavailable.

3. **State Management**
   3.1 Persist per-user stats (`love_integrity`, `temptation`, `career_status`, `energy`), flags (met characters, relationships, unlocked packs), chapter progress, and timestamps.
   3.2 Apply choice effects atomically, recalculate stats, and guard against negative energy.
   3.3 Provide `/profile` command returning chapter, stat summary, titles, and premium ownership.

4. **Monetization**
   4.1 Implement premium pack metadata and entitlement checks before showing gated scenes/choices.
   4.2 Surface at least one premium route and one premium boost choice in the MVP chapter.
   4.3 Support energy refills (time-based regeneration plus purchase option) configurable per environment.
   4.4 Integrate Telegram Payments using a supported provider (e.g., Stripe) with USD pricing at launch; enable EUR plus one configurable local currency (INR/BRL/TRY based on priority market) when metadata is ready.
   4.5 Log monetization funnel events server-side (`premium_paywall_shown`, `purchase_initiated`, `purchase_success`) and forward to the analytics stack.

5. **Retention Mechanics**
   5.1 Track daily logins and award configurable bonuses (energy, special choices).
   5.2 Provide hooks for weekly events via flags that unlock limited scenes.
   5.3 Broadcast announcements via linked Telegram channel when configured.

6. **Analytics & Telemetry**
   6.1 Log all key funnel events server-side into `analytics_events` (fields: `user_id`, `timestamp`, `event_type`, `properties` JSON).
   6.2 Emit at minimum: `/start` received, tutorial completed, Chapter 1 completed, premium paywall shown, purchase initiated, purchase success, scene viewed, and choice made.
   6.3 Provide a pluggable dispatcher to forward the same events to Amplitude or Mixpanel SDKs when credentials are configured.

7. **Performance & Reliability**
   7.1 Respond to user interactions in <2 seconds under normal load.
   7.2 Handle duplicate callback deliveries idempotently.
   7.3 Log errors with enough context (user ID, scene ID, choice) for debugging.

8. **Content Scope**
   8.1 Deliver 8–12 tutorial scenes covering onboarding, stat intro, and first temptation.
   8.2 Ship Chapter 1 (“Neon Nights & Notifications”) with 20–30 scenes on the free path.
   8.3 Build the first premium romance route with at least 30 scenes, 5 premium-only decision points, and 2 materially different endings (minimum 3–4 acts).

## 5. Non-Goals / Out of Scope

- Natural language parsing of arbitrary text responses (stick to inline choices in v1).
- Multiplayer/group chat scenes (only 1:1 chats for MVP).
- Advanced AI-generated story content; all scenes are authored manually.
- Cross-platform clients outside Telegram.

## 6. Design Considerations

- Tone: neon cyberpunk romance; short 2–5 minute sessions.
- Inline keyboards should prioritize 2–4 concise options, using emoji to indicate stat impact when helpful.
- Surface stat deltas periodically via lightweight HUD snippets (e.g., “❤️ +5 | 🔥 +2”).
- Premium choices should clearly explain benefits before purchase.
- English-only UI and story content for v1; author scenes to allow future localization by storing text outside business logic.

## 7. Technical Considerations

- Recommended stack: Python with `python-telegram-bot` or `aiogram`; PostgreSQL/Redis for state persistence.
- Use long polling for development, configurable to switch to webhook mode for production.
- Keep app servers stateless; store state in DB with optimistic concurrency or row-level locking.
- Payments use Telegram Payments API; store premium entitlements server-side and support USD at launch with extensible metadata for EUR plus one prioritized local currency.
- Ensure configuration separates dev/test/prod tokens and payment providers.
- Persist analytics events in Postgres (or equivalent) and support optional ingestion to Amplitude/Mixpanel for funnel analysis.

## 8. Success Metrics

- 80% of new users complete the tutorial within first session.
- ≥40% of users return within 7 days (rolling retention) once live.
- ≥5% of active users engage with at least one premium choice/route.
- Error rate for callbacks <0.5% per day.

## 9. Open Questions

1. Which optional analytics platform (Amplitude vs. Mixpanel vs. internal-only) should be activated first?
2. Which local currency (INR, BRL, TRY, etc.) should ship alongside USD/EUR at launch?
3. What is the timeline for adding the first additional localization after English?
4. Who owns the banned-word list maintenance for name sanitization?