Below is a compact PRD you can code from, plus a high‑level view of how the coding will work for a **Telegram chat-based simulation game** (“futuristic city looking for love but full of temptations”).

Citations below reference general patterns for Telegram game bots and interactive fiction games [1][3].

---

## 1. Product Requirements Document (PRD)

### 1.1. Product Summary

- **Product**: Telegram chat-based simulation game bot.
- **Theme**: Futuristic neon city; the player is trying to find genuine love while navigating career, status, and constant temptations (flings, fame, power, AI lovers, etc.).
- **Platform**: Telegram Bot API, 1:1 chats first; optionally groups later.
- **Monetization**: In‑bot purchases (premium story paths, character packs, cosmetics, energy/time skips).

The bot is a **stateful, text-first interactive fiction game**: the bot sends narrative text + inline keyboards; the user chooses options; the game updates their state and continues the story in real time [1][3].

---

### 1.2. User Personas

1. **Romance/Story Gamer**
   - Likes visual novels, interactive fiction, otome/romance games.
   - Plays in short sessions (2–5 minutes).
   - Motivated by emotional arcs, choices, and endings.

2. **Sci‑Fi / Cyberpunk Fan**
   - Drawn to futuristic city setting and tech themes.
   - Enjoys moral dilemmas (AI partners, loyalty vs. pleasure).

3. **Telegram Native User**
   - Prefers not installing extra apps.
   - Discovering the game via word of mouth, channels, or groups.

---

### 1.3. Core Game Loop

1. Player sends `/start`.
2. Bot sets up profile (name, pronouns, basic archetype).
3. Bot presents **scene** (short narrative chunk).
4. Bot shows **2–4 choices via inline keyboard** (e.g., “Flirt”, “Focus on work”, “Ghost them”).
5. Player taps a choice → bot:
   - Updates **game state** (relationship score, temptation score, career, etc.).
   - Logs progress (chapter, flags).
   - Returns new scene + new choices.
6. Periodically:
   - Unlocks achievements / titles.
   - Nudges toward monetized features (premium routes, extra energy, special scenes).

Repeat in sessions until chapter/arc completion.

---

### 1.4. Game Structure

#### 1.4.1. State Model (per user)

Store (e.g., in a DB):

- `user_id` (Telegram ID)
- `current_scene_id`
- `chapter` / `season`
- Stats:
  - `love_integrity` (0–100)
  - `temptation` (0–100)
  - `career_status` (0–100)
  - `energy` (actions per period)
- Flags:
  - `met_character_X`
  - `in_relationship_with_Y`
  - `premium_unlocked_packs` (list)
- Meta:
  - `last_active_at`
  - `tutorial_completed`

#### 1.4.2. Scenes & Choices

Represent scenes as structured data (JSON, DB, or Python dicts):

```json
{
  "id": "intro_01",
  "text": "Neon rain hits the glass as your wrist‑implant buzzes. A message: 'I saw you tonight. Coffee?'",
  "choices": [
    {
      "id": "intro_01_reply_yes",
      "label": "Reply: 'Sure, when?'",
      "effects": {
        "love_integrity": +5,
        "temptation": +2
      },
      "next_scene_id": "cafe_meet_01"
    },
    {
      "id": "intro_01_reply_no",
      "label": "Ignore the message",
      "effects": {
        "love_integrity": -5,
        "career_status": +3
      },
      "next_scene_id": "work_focus_01"
    }
  ]
}
```

Monetized choices are marked, e.g., `"requires_premium_pack": "office_romance"`.

#### 1.4.3. Chapters / Arcs

- **Tutorial**: Establish city, stakes, first temptation, first meaningful love interest.
- **Core Chapters**:
  - “Neon Nights & Notifications” (balancing work, nightlife, and dating apps).
  - “Ghosts in the Network” (AI temptations vs human trust).
  - “Public Scandal” (paparazzi, social reputation).
- **Endings**:
  - “True Love in the Neon” (high love_integrity, low temptation).
  - “Alone at the Top” (high career, high temptation, low love).
  - “Digital Obsession” (high AI intimacy, low real connections).

---

### 1.5. Key Features

#### 1.5.1. Onboarding

- `/start`:
  - Intro scene
  - 2–3 quick questions to personalize:
    - Name
    - Preferred pronouns / type of partner(s)
  - First choice within 60 seconds.

#### 1.5.2. Core Gameplay Features

- Interactive fiction with inline keyboards (no free‑form text parsing in v1; avoid NLP complexity).
- Basic stats visibly surfaced at key points:
  - “Loyalty vs. Temptation meter”
  - “Career standing”
- Simple profile command: `/profile` shows:
  - Current chapter
  - Main stats
  - Titles/unlocks.

#### 1.5.3. Monetization Mechanics

- **Premium Routes**:
  - Lock certain story arcs behind a one‑time purchase (per theme pack).
- **Premium Choices**:
  - Occasionally show a premium button:
    - e.g., “Book a secret rooftop dinner (Premium)” → richer scene + stat boost.
- **Energy System (Optional in v1)**:
  - Each choice consumes `energy`.
  - Refill over time or by purchase.
- Implement server-side entitlement checks; mark which packs a user owns.

#### 1.5.4. Retention Mechanics

- Daily login bonus (extra energy or a free special choice).
- Weekly events/seasons (just flags that enable specific scenes/quests).
- Broadcast updates via a companion **Telegram channel**.

---

### 1.6. Non‑Functional Requirements

- **Tech stack (example)**:
  - Backend: Python (e.g., `python-telegram-bot` or `aiogram`) or Node.js.
  - DB: PostgreSQL / MongoDB / Redis (any key‑value or relational DB fine).
- **Performance**:
  - Response time < 1–2 seconds.
- **Scalability**:
  - Stateless app servers; state in DB.
- **Reliability**:
  - Graceful handling of unexpected inputs.
  - Idempotent callbacks for inline keyboard presses.

---

## 2. How the Coding Part Works (High-Level)

Below assumes Python + Telegram Bot API, but the logic is similar in any language [1][3].

### 2.1. Set Up the Bot

1. Create bot via **@BotFather**, get `BOT_TOKEN`.
2. In your code:
   - Use long polling (simpler for dev) or webhook (better for production).
3. Install a library:
   - `pip install python-telegram-bot` (or `aiogram`).

### 2.2. Main Components

1. **Update Handler**  
   Listens for:
   - Messages (like `/start`, `/profile`).
   - Callback queries (button taps from inline keyboards).

2. **State Manager**  
   Responsible for:
   - Loading user state from DB.
   - Applying effects (stat changes, unlocking flags).
   - Saving state back.
   - Knowing which scene to show next.

3. **Scene Engine**  
   - Given `current_scene_id` and a **choice**, computes:
     - New stats
     - Next scene ID
   - Returns text + keyboard layout.

4. **Payment / Monetization Handler**  
   - Integrates Telegram’s payment API or external billing flow.
   - When payment succeeds:
     - Mark `premium_unlocked_packs` for that user in DB.

---

### 2.3. Basic Flow in Code (Pseudo-Python)

```python
def start_handler(update, context):
    user_id = update.effective_user.id
    user_state = load_or_create_user(user_id)

    user_state.current_scene_id = "intro_01"
    save_user_state(user_state)

    send_scene(update, context, user_state.current_scene_id, user_state)


def button_callback_handler(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    choice_id = query.data  # e.g. "intro_01_reply_yes"

    user_state = load_user_state(user_id)

    # 1. Resolve choice → effects + next_scene
    scene = SCENES[user_state.current_scene_id]
    choice = get_choice(scene, choice_id)

    # 2. Apply effects
    apply_choice_effects(user_state, choice)

    # 3. Update scene
    user_state.current_scene_id = choice["next_scene_id"]
    save_user_state(user_state)

    # 4. Edit message or send new one with next scene
    send_scene(update, context, user_state.current_scene_id, user_state)
```

`send_scene()`:

- Looks up scene text.
- Builds inline keyboard buttons corresponding to available choices.
- Optionally marks premium choices differently and checks entitlements.

This is a classic pattern: **stateful Telegram bot game with inline keyboards** where your “game logic and rules” are defined in code/data structures that the bot uses to respond in real time [3].

---

### 2.4. Defining Game Logic

You:

1. Create a set of **scene definitions** (like the JSON above).
2. Implement a function that:
   - Takes `current_scene_id` and `choice_id`.
   - Validates choice.
   - Applies stat changes.
   - Returns `next_scene_id`.
3. Optionally add:
   - Conditions (e.g., only show some choices if `love_integrity > 50`).
   - Random events.

This is exactly what “create the game logic and rules” means in practice: formalizing how players move between states and how their stats change as they interact [3].

---

### 2.5. Payments in Code (Outline)

- Use Telegram’s Payments API or another payment provider.
- Typical steps:
  1. Player chooses a “Buy premium pack” button.
  2. Bot sends an invoice or payment link.
  3. On successful payment, your webhook:
     - Confirms payment.
     - Updates `premium_unlocked_packs` for that user.
  4. Scene engine then allows access to premium routes/choices.

---

### 2.6. Development Milestones

1. **MVP**
   - `/start`, `/profile`
   - Tutorial + 1 short chapter
   - Inline keyboards working
   - Simple DB for state
2. **Add Monetization**
   - 1 premium route
   - Payment handler
3. **Add More Content**
   - 2–3 more chapters
   - Events & retention loops
4. **Polish**
   - Better copy, balancing stats, analytics.

---

If you’d like, next I can:

- Turn this into a **concrete file/folder structure** for your project (e.g., `scenes.py`, `state.py`, `handlers.py`),  
- Or draft a **minimal working Python script** skeleton you can extend with your own scenes and monetization logic.p