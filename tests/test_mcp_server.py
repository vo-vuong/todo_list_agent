from __future__ import annotations

import anyio
from datetime import date

from daily_planner_agent import mcp_server
from daily_planner_agent.models import Task


def test_complete_task_by_reference_completes_exact_task_id(monkeypatch) -> None:
    task = Task(
        id="today",
        title="Review planner requirements",
        due_date=date(2026, 6, 11),
        estimated_minutes=30,
        priority="medium",
        completed=False,
    )

    monkeypatch.setattr(mcp_server, "store_list_tasks", lambda include_completed=True: [task])
    monkeypatch.setattr(
        mcp_server,
        "store_complete_task",
        lambda task_id: task.model_copy(update={"completed": True}),
    )

    result = mcp_server.complete_task_by_reference_result("today")

    assert result["status"] == "completed"
    assert result["task"]["id"] == "today"
    assert result["task"]["completed"] is True


def test_complete_task_by_reference_rejects_ambiguous_title(monkeypatch) -> None:
    tasks = [
        Task(
            id="task-1",
            title="Review planner requirements",
            due_date=date(2026, 6, 11),
            estimated_minutes=30,
            priority="medium",
            completed=False,
        ),
        Task(
            id="task-2",
            title="Review planner requirements",
            due_date=date(2026, 6, 11),
            estimated_minutes=45,
            priority="high",
            completed=False,
        ),
    ]
    completed: list[str] = []

    monkeypatch.setattr(mcp_server, "store_list_tasks", lambda include_completed=True: tasks)
    monkeypatch.setattr(mcp_server, "store_complete_task", lambda task_id: completed.append(task_id))

    result = mcp_server.complete_task_by_reference_result("Review planner requirements")

    assert result["status"] == "needs_clarification"
    assert "Multiple incomplete tasks" in result["message"]
    assert [match["id"] for match in result["matches"]] == ["task-1", "task-2"]
    assert completed == []


def test_mcp_tool_descriptions_guide_agent_tool_selection() -> None:
    async def list_tools():
        return await mcp_server.create_mcp_server().list_tools()

    tools = {tool.name: tool.description or "" for tool in anyio.run(list_tools)}

    assert "preferred completion tool" in tools["complete_task_by_reference"]
    assert "task ID or by unique incomplete task title" in tools["complete_task_by_reference"]
    assert "needs_clarification" in tools["complete_task_by_reference"]
    assert "daily plan markdown report" in tools["generate_daily_report"]
    assert "writes reports/daily-plan-YYYY-MM-DD.md" in tools["generate_daily_report"]
    assert "read-only tool" in tools["list_tasks"]
