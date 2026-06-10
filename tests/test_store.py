from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from daily_planner_agent.store import (
    TaskNotFoundError,
    add_task,
    complete_task,
    list_tasks,
    list_todays_tasks,
    reset_tasks,
)


def test_list_todays_tasks_includes_overdue_and_today_only(tmp_path: Path) -> None:
    path = _write_tasks(tmp_path)

    tasks = list_todays_tasks(today=date(2026, 6, 10), path=path)

    assert [task.id for task in tasks] == ["overdue", "today"]


def test_add_task_validates_priority_and_writes_file(tmp_path: Path) -> None:
    path = _write_tasks(tmp_path)

    task = add_task(
        title="New task",
        description="Added in test",
        due_date="2026-06-10",
        estimated_minutes=20,
        priority="medium",
        path=path,
    )

    tasks = list_tasks(path=path)
    assert task.id.startswith("task-")
    assert tasks[-1].title == "New task"

    with pytest.raises(ValueError):
        add_task(
            title="Bad task",
            due_date="2026-06-10",
            estimated_minutes=20,
            priority="urgent",  # type: ignore[arg-type]
            path=path,
        )


def test_complete_task_marks_task_completed(tmp_path: Path) -> None:
    path = _write_tasks(tmp_path)

    task = complete_task("today", path=path)

    assert task.completed is True
    assert next(item for item in list_tasks(path=path) if item.id == "today").completed is True


def test_complete_task_rejects_unknown_id(tmp_path: Path) -> None:
    path = _write_tasks(tmp_path)

    with pytest.raises(TaskNotFoundError):
        complete_task("missing", path=path)


def test_reset_tasks_restores_sample_data(tmp_path: Path) -> None:
    sample_path = _write_tasks(tmp_path, name="tasks.sample.json")
    path = tmp_path / "tasks.json"
    path.write_text("[]\n", encoding="utf-8")

    tasks = reset_tasks(path=path, sample_path=sample_path)

    assert [task.id for task in tasks] == ["overdue", "today", "future", "completed"]
    assert json.loads(path.read_text(encoding="utf-8")) == json.loads(
        sample_path.read_text(encoding="utf-8")
    )


def _write_tasks(tmp_path: Path, name: str = "tasks.json") -> Path:
    path = tmp_path / name
    payload = [
        {
            "id": "overdue",
            "title": "Overdue task",
            "description": "",
            "due_date": "2026-06-09",
            "estimated_minutes": 30,
            "priority": "high",
            "completed": False,
        },
        {
            "id": "today",
            "title": "Today task",
            "description": "",
            "due_date": "2026-06-10",
            "estimated_minutes": 45,
            "priority": "medium",
            "completed": False,
        },
        {
            "id": "future",
            "title": "Future task",
            "description": "",
            "due_date": "2026-06-11",
            "estimated_minutes": 20,
            "priority": "low",
            "completed": False,
        },
        {
            "id": "completed",
            "title": "Completed task",
            "description": "",
            "due_date": "2026-06-10",
            "estimated_minutes": 15,
            "priority": "medium",
            "completed": True,
        },
    ]
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
