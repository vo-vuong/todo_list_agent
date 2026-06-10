from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from daily_planner_agent.chat_agent import ChatMessage, ChatTaskResult, TaskDraft, _build_chat_prompt


def test_task_draft_converts_to_task_create_without_defaulting_priority() -> None:
    draft = TaskDraft(
        title="Prepare slides",
        due_date=date(2026, 6, 12),
        estimated_minutes=45,
        priority="high",
    )

    task = draft.to_task_create()

    assert task.title == "Prepare slides"
    assert task.due_date == date(2026, 6, 12)
    assert task.estimated_minutes == 45
    assert task.priority == "high"


def test_chat_result_requires_follow_up_for_missing_fields() -> None:
    result = ChatTaskResult(
        follow_up_question="When is this due and what priority should it have?",
        missing_fields=["due_date", "priority"],
    )

    assert result.draft is None
    assert result.missing_fields == ["due_date", "priority"]


def test_chat_result_rejects_empty_result() -> None:
    with pytest.raises(ValidationError):
        ChatTaskResult()


def test_build_chat_prompt_includes_date_and_conversation() -> None:
    prompt = _build_chat_prompt(
        [ChatMessage(role="user", content="Create a high priority task for tomorrow, 30 minutes.")],
        date(2026, 6, 11),
    )

    assert "Current local date: 2026-06-11" in prompt
    assert "user: Create a high priority task" in prompt
    assert "title, due_date, estimated_minutes, and priority" in prompt
