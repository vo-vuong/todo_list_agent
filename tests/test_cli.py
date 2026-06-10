from __future__ import annotations

from datetime import date

import pytest

from daily_planner_agent import cli
from daily_planner_agent.models import DailyPlan, Task


@pytest.mark.anyio
async def test_run_plan_completes_before_planning_and_writes_report(monkeypatch, tmp_path) -> None:
    calls: list[str] = []

    async def fake_complete_task(task_id: str) -> Task:
        calls.append(f"complete:{task_id}")
        return Task(
            id=task_id,
            title="Done",
            description="",
            due_date=date(2026, 6, 11),
            estimated_minutes=10,
            priority="high",
            completed=True,
        )

    async def fake_list_todays_tasks() -> list[Task]:
        calls.append("list")
        return []

    async def fake_generate_daily_plan(tasks: list[Task]) -> DailyPlan:
        calls.append(f"plan:{len(tasks)}")
        return DailyPlan(plan_date=date(2026, 6, 11), summary="No tasks.")

    def fake_require_openai_api_key() -> None:
        calls.append("key")

    def fake_write_markdown_report(plan: DailyPlan):
        calls.append("write")
        path = tmp_path / "daily-plan-2026-06-11.md"
        path.write_text("report", encoding="utf-8")
        return path

    monkeypatch.setattr(cli, "complete_task", fake_complete_task)
    monkeypatch.setattr(cli, "list_todays_tasks", fake_list_todays_tasks)
    monkeypatch.setattr(cli, "generate_daily_plan", fake_generate_daily_plan)
    monkeypatch.setattr(cli, "require_openai_api_key", fake_require_openai_api_key)
    monkeypatch.setattr(cli, "write_markdown_report", fake_write_markdown_report)

    result = await cli.run_plan(complete_task_id="today-medium")

    assert result == 0
    assert calls == ["key", "complete:today-medium", "list", "plan:0", "write"]
