from __future__ import annotations

from datetime import date

import anyio
import pytest
from pydantic import ValidationError

from daily_planner_agent.config import McpServerSettings, OpenAISettings
from daily_planner_agent import chat_agent
from daily_planner_agent.chat_agent import (
    ChatActionAgentOutput,
    ChatActionTrace,
    ChatMessage,
    ChatTaskResult,
    TaskDraft,
    _build_action_prompt,
    _build_chat_prompt,
    _build_process_tool_call,
    looks_like_action_request,
)


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


def test_action_prompt_includes_discovered_tools() -> None:
    prompt = _build_action_prompt(
        [ChatMessage(role="user", content="Complete today-medium and export markdown.")],
        date(2026, 6, 11),
        ["list_tasks", "complete_task_by_reference", "generate_daily_report"],
    )

    assert "Current local date: 2026-06-11" in prompt
    assert "- complete_task_by_reference" in prompt
    assert "- generate_daily_report" in prompt
    assert "Use the MCP tools" in prompt


def test_looks_like_action_request_detects_complete_and_report_commands() -> None:
    assert looks_like_action_request("Hoàn thành Review planner requirements")
    assert looks_like_action_request("Xuất file plan markdown")
    assert not looks_like_action_request("Create a high priority task for tomorrow")


def test_process_tool_call_records_selected_tool_arguments_and_result_summary() -> None:
    trace = ChatActionTrace(discovered_tools=["complete_task_by_reference", "generate_daily_report"])
    process_tool_call = _build_process_tool_call(trace)

    async def fake_call_tool(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
        return {"status": "completed", "message": f"{tool_name} ok", "arguments": arguments}

    result = anyio.run(process_tool_call, None, fake_call_tool, "complete_task_by_reference", {"reference": "today"})

    assert result["status"] == "completed"
    assert [call.tool_name for call in trace.calls] == ["complete_task_by_reference"]
    assert trace.calls[0].arguments == {"reference": "today"}
    assert trace.calls[0].result_summary == "completed: complete_task_by_reference ok"


def test_process_tool_call_preserves_multi_tool_order() -> None:
    trace = ChatActionTrace(discovered_tools=["complete_task_by_reference", "generate_daily_report"])
    process_tool_call = _build_process_tool_call(trace)

    async def fake_call_tool(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
        return {"status": "ok", "message": tool_name}

    anyio.run(process_tool_call, None, fake_call_tool, "complete_task_by_reference", {"reference": "today"})
    anyio.run(process_tool_call, None, fake_call_tool, "generate_daily_report", {})

    assert [call.tool_name for call in trace.calls] == [
        "complete_task_by_reference",
        "generate_daily_report",
    ]


def test_run_chat_action_discovers_mcp_tools_before_agent_run(monkeypatch) -> None:
    events: list[str] = []

    class Tool:
        name = "complete_task_by_reference"

    class FakeToolset:
        def __init__(self, url: str, *, process_tool_call, cache_tools: bool) -> None:
            events.append(f"toolset:{url}:{cache_tools}")
            self.process_tool_call = process_tool_call

    class FakeAgent:
        def __init__(self, *_args, toolsets: list[FakeToolset], **_kwargs) -> None:
            events.append("agent_init")
            self.toolset = toolsets[0]

        async def run(self, _prompt: str):
            events.append("run")

            async def fake_call_tool(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
                return {"status": "completed", "message": "Completed task today."}

            await self.toolset.process_tool_call(
                None,
                fake_call_tool,
                "complete_task_by_reference",
                {"reference": "today"},
            )
            return type("Result", (), {"output": ChatActionAgentOutput(message="Done.")})()

    async def fake_discover_tools() -> list[Tool]:
        events.append("discover")
        return [Tool()]

    monkeypatch.setattr(chat_agent, "require_openai_api_key", lambda: OpenAISettings("key", "gpt-5-nano"))
    monkeypatch.setattr(
        chat_agent,
        "get_mcp_server_settings",
        lambda: McpServerSettings("http://localhost:8000/sse", "localhost", 8000, "/sse"),
    )
    monkeypatch.setattr(chat_agent, "discover_tools", fake_discover_tools)
    monkeypatch.setattr(chat_agent, "OpenAIProvider", lambda api_key: object())
    monkeypatch.setattr(chat_agent, "OpenAIResponsesModel", lambda model, provider: object())
    monkeypatch.setattr(chat_agent, "MCPToolset", FakeToolset)
    monkeypatch.setattr(chat_agent, "Agent", FakeAgent)

    result = anyio.run(
        chat_agent.run_chat_action_from_chat,
        [ChatMessage(role="user", content="Complete today")],
    )

    assert events == ["discover", "toolset:http://localhost:8000/sse:False", "agent_init", "run"]
    assert result.trace.discovered_tools == ["complete_task_by_reference"]
    assert result.trace.calls[0].tool_name == "complete_task_by_reference"
