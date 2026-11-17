import os
from unittest.mock import patch

from src.explain import generate_explanation
from src.retrieval import KnowledgeBase

SONG = {"id": "2", "title": "Midnight Coding", "artist": "LoRoom", "genre": "lofi", "mood": "chill"}
USER_PREFS = {"genre": "lofi", "mood": "chill"}
REASONS = "genre match, mood match"


def test_falls_back_to_deterministic_explanation_without_api_key():
    kb = KnowledgeBase()
    with patch.dict(os.environ, {}, clear=True):
        result = generate_explanation(kb, USER_PREFS, SONG, 0.9, REASONS)

    assert result.used_llm is False
    assert result.grounded is True
    assert "genre match, mood match" in result.text


def test_falls_back_when_api_call_raises():
    kb = KnowledgeBase()
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}):
        with patch("src.explain._call_claude", side_effect=RuntimeError("network down")):
            result = generate_explanation(kb, USER_PREFS, SONG, 0.9, REASONS)

    assert result.used_llm is False
    assert result.grounded is True


def test_falls_back_when_generated_text_is_ungrounded():
    kb = KnowledgeBase()
    fabricated = "Recorded live in Tokyo in 1998 with a Grammy-winning saxophone solo."
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}):
        with patch("src.explain._call_claude", return_value=fabricated):
            result = generate_explanation(kb, USER_PREFS, SONG, 0.9, REASONS)

    assert result.used_llm is True
    assert result.grounded is False
    assert result.text != fabricated
