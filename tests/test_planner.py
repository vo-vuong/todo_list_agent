from __future__ import annotations

from daily_planner_agent.config import OpenAISettings
from daily_planner_agent import planner
from daily_planner_agent.planner import MissingOpenAIKeyError, require_openai_api_key


def test_require_openai_api_key_rejects_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(
        planner,
        "get_openai_settings",
        lambda: OpenAISettings(api_key=None, model="gpt-5-nano"),
    )

    try:
        require_openai_api_key()
    except MissingOpenAIKeyError as exc:
        assert "OPENAI_API_KEY is required" in str(exc)
    else:
        raise AssertionError("Expected MissingOpenAIKeyError")
