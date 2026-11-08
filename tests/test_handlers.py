"""Tests for handler registration and placeholder logic."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler

from bot.handlers import register_handlers
from bot.handlers import profile as profile_handlers
from bot.handlers import start as start_handlers


class DummyChat:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []
        self.id = 1

    async def send_message(self, text: str, reply_markup=None, parse_mode=None) -> None:
        self.messages.append({"text": text, "reply_markup": reply_markup, "parse_mode": parse_mode})


class DummyUpdate:
    def __init__(self, chat: DummyChat) -> None:
        self.effective_chat = chat
        self.effective_user = SimpleNamespace(id=123)


class DummyMessage:
    def __init__(self, text: str | None) -> None:
        self.text = text
        self.replies: list[dict[str, object]] = []

    async def reply_text(self, text: str, reply_markup=None) -> None:
        self.replies.append({"text": text, "reply_markup": reply_markup})


class DummyCallbackQuery:
    def __init__(self, data: str) -> None:
        self.data = data
        self.answered = False
        self.edited_message: str | None = None

    async def answer(self) -> None:
        self.answered = True

    async def edit_message_text(self, text: str) -> None:
        self.edited_message = text


class FakeApplication:
    def __init__(self) -> None:
        self.handlers: list[object] = []

    def add_handler(self, handler) -> None:  # pragma: no cover - trivial helper
        self.handlers.append(handler)


def test_register_handlers_adds_start_and_profile_handlers(sanitizer, state_store, scene_loader):
    app = FakeApplication()

    register_handlers(app, sanitizer, state_store, scene_loader)

    assert any(isinstance(handler, ConversationHandler) for handler in app.handlers)
    assert any(
        isinstance(handler, CommandHandler) and "profile" in handler.commands
        for handler in app.handlers
    )


@pytest.mark.asyncio
async def test_start_handler_prompts_for_name(sanitizer, state_store, scene_loader):
    conversation = start_handlers.build_handlers(sanitizer, state_store, scene_loader)[0]
    start_handler = conversation.entry_points[0]
    chat = DummyChat()
    update = DummyUpdate(chat)
    context = SimpleNamespace(user_data={})

    state = await start_handler.callback(update, context)

    assert state == start_handlers.ASK_NAME
    assert "Tell me the name" in chat.messages[0]["text"]


@pytest.mark.asyncio
async def test_profile_handler_reports_real_stats(state_store):
    # Create a user first
    from bot.state import UserState
    user_state = UserState(
        user_id=123,
        player_name="Nova",
        player_pronoun="they_them",
        current_scene_id="test_scene",
        current_chapter_id="chapter_tutorial",
    )
    state_store.save_user_state(user_state)
    
    handler = profile_handlers.build_handlers(state_store)[0]
    chat = DummyChat()
    update = DummyUpdate(chat)
    context = SimpleNamespace(user_data={})

    await handler.callback(update, context)

    assert chat.messages, "Profile handler did not emit a message"
    message = chat.messages[0]["text"]
    assert "Nova" in message
    assert "They / Them" in message
    for stat_label in ("Love Integrity", "Temptation", "Career Status", "Night Cycles"):
        assert stat_label in message


@pytest.mark.asyncio
async def test_collect_name_sanitizes_and_prompts(sanitizer, state_store, scene_loader):
    conversation = start_handlers.build_handlers(sanitizer, state_store, scene_loader)[0]
    name_handler = conversation.states[start_handlers.ASK_NAME][0]
    message = DummyMessage("<b> Nova </b>")
    update = SimpleNamespace(
        message=message,
        effective_chat=SimpleNamespace(id=99),
        effective_user=SimpleNamespace(id=42),
    )
    context = SimpleNamespace(user_data={})

    state = await name_handler.callback(update, context)

    assert state == start_handlers.ASK_PRONOUN
    assert context.user_data["player_name"] == "Nova"
    assert message.replies, "No reply was sent after collecting name"
    reply = message.replies[0]
    assert "Nice to meet you, Nova!" in reply["text"]
    assert isinstance(reply["reply_markup"], InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_collect_name_rejects_invalid_length(sanitizer, state_store, scene_loader):
    conversation = start_handlers.build_handlers(sanitizer, state_store, scene_loader)[0]
    name_handler = conversation.states[start_handlers.ASK_NAME][0]
    message = DummyMessage("x")
    update = SimpleNamespace(
        message=message,
        effective_chat=SimpleNamespace(id=99),
        effective_user=SimpleNamespace(id=42),
    )
    context = SimpleNamespace(user_data={})

    state = await name_handler.callback(update, context)

    assert state == start_handlers.ASK_NAME
    assert "player_name" not in context.user_data
    assert message.replies and str(message.replies[0]["text"]).startswith("⚠️")


class DummyBot:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    async def send_message(self, chat_id: int, text: str, reply_markup=None) -> None:
        self.messages.append({"chat_id": chat_id, "text": text, "reply_markup": reply_markup})


@pytest.mark.asyncio
async def test_collect_pronoun_records_choice_and_confirms(sanitizer, state_store, tmp_path):
    # Create scene loader with test scene file
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    test_scene = {
        "scenes": [
            {
                "id": "chapter_tutorial_intro",
                "narrative": {"en": "Welcome, {player_name}!"},
                "choices": [{"id": "c1", "text": {"en": "Continue"}, "next_scene_id": "next"}]
            }
        ]
    }
    import json
    (scenes_dir / "chapter_tutorial.json").write_text(json.dumps(test_scene), encoding="utf-8")
    
    from bot.scenes import SceneLoader
    scene_loader = SceneLoader(str(scenes_dir))
    
    conversation = start_handlers.build_handlers(sanitizer, state_store, scene_loader)[0]
    pronoun_handler = conversation.states[start_handlers.ASK_PRONOUN][0]
    callback_query = DummyCallbackQuery("pronoun:they_them")
    bot = DummyBot()
    update = SimpleNamespace(
        callback_query=callback_query,
        effective_chat=SimpleNamespace(id=99),
        effective_user=SimpleNamespace(id=42),
    )
    context = SimpleNamespace(user_data={"player_name": "Nova"}, bot=bot)

    state = await pronoun_handler.callback(update, context)

    assert state == ConversationHandler.END
    assert context.user_data["player_pronoun"] == "they_them"
    assert callback_query.answered, "Callback query was not acknowledged"
    assert callback_query.edited_message
    assert "They / Them" in callback_query.edited_message
    # Verify state was saved
    saved_state = state_store.load_user_state(42)
    assert saved_state is not None
    assert saved_state.player_name == "Nova"
    assert saved_state.player_pronoun == "they_them"
