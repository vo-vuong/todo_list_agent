from __future__ import annotations

from datetime import date
from pathlib import Path

from daily_planner_agent.config import report_path_for_date
from daily_planner_agent.models import DailyPlan


def render_markdown_report(plan: DailyPlan) -> str:
    lines = [
        f"# Daily Plan - {plan.plan_date.isoformat()}",
        "",
        "## Summary",
        "",
        plan.summary,
        "",
        "## Time Blocks",
        "",
        "| Time | Task | Priority | Notes |",
        "|---|---|---|---|",
    ]

    if plan.time_blocks:
        for block in plan.time_blocks:
            lines.append(
                "| "
                f"{_format_time(block.start_time)}-{_format_time(block.end_time)} | "
                f"{_escape_table(block.title)} (`{block.task_id}`) | "
                f"{block.priority} | "
                f"{_escape_table(block.notes)} |"
            )
    else:
        lines.append("| - | No scheduled tasks | - | - |")

    lines.extend(["", "## Unscheduled overflow", ""])
    if plan.unscheduled_overflow:
        for item in plan.unscheduled_overflow:
            lines.append(f"- `{item.task_id}` {item.title} ({item.priority}): {item.reason}")
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def write_markdown_report(plan: DailyPlan) -> Path:
    path = report_path_for_date(plan.plan_date.isoformat())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown_report(plan), encoding="utf-8")
    return path


def report_exists_for_date(plan_date: date) -> Path:
    return report_path_for_date(plan_date.isoformat())


def _format_time(value: object) -> str:
    return getattr(value, "strftime")("%H:%M")


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")
