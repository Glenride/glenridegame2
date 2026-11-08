"""Tests for onboarding sanitizer."""

from __future__ import annotations

import pytest

from bot.onboarding import OnboardingValidationError


def test_sanitize_name_strips_markup(sanitizer):
    assert sanitizer.sanitize_name("<b> Neo *</b>") == "Neo"


@pytest.mark.parametrize("candidate", ["x", "", None])
def test_sanitize_name_enforces_length(sanitizer, candidate):
    with pytest.raises(OnboardingValidationError):
        sanitizer.sanitize_name(candidate)  # type: ignore[arg-type]


def test_sanitize_name_blocks_banned_words(sanitizer):
    with pytest.raises(OnboardingValidationError):
        sanitizer.sanitize_name("Mega slur lord")


def test_validate_pronoun_accepts_known_codes(sanitizer):
    assert sanitizer.validate_pronoun("she_her") == "She / Her"


def test_validate_pronoun_rejects_unknown(sanitizer):
    with pytest.raises(OnboardingValidationError):
        sanitizer.validate_pronoun("unknown")
