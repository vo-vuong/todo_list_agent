from __future__ import annotations

from datetime import date, time

from daily_planner_agent.models import DailyPlan, OverflowTask, ScheduleBlock
from daily_planner_agent.reporting import render_markdown_report


def test_render_markdown_report_has_required_sections() -> None:
    plan = DailyPlan(
        plan_date=date(2026, 6, 11),
        summary="Focus on the urgent work first.",
        time_blocks=[
            ScheduleBlock(
                task_id="overdue-high",
                title="Submit status update",
                priority="high",
                start_time=time(9, 0),
                end_time=time(9, 30),
                notes="Handle first.",
            )
        ],
        unscheduled_overflow=[
            OverflowTask(
                task_id="future-low",
                title="Prepare tomorrow notes",
                priority="low",
                reason="Not enough available focus time.",
            )
        ],
    )

    markdown = render_markdown_report(plan)

    assert "# Daily Plan - 2026-06-11" in markdown
    assert "## Summary" in markdown
    assert "## Time Blocks" in markdown
    assert "| 09:00-09:30 | Submit status update (`overdue-high`) | high | Handle first. |" in markdown
    assert "## Unscheduled overflow" in markdown
    assert "`future-low` Prepare tomorrow notes" in markdown


def test_daily_plan_rejects_lunch_overlap() -> None:
    try:
        DailyPlan(
            plan_date=date(2026, 6, 11),
            summary="Bad lunch schedule.",
            time_blocks=[
                ScheduleBlock(
                    task_id="today-medium",
                    title="Review planner requirements",
                    priority="medium",
                    start_time=time(11, 30),
                    end_time=time(12, 15),
                )
            ],
        )
    except ValueError as exc:
        assert "lunch" in str(exc)
    else:
        raise AssertionError("Expected lunch overlap validation error")
