from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from daily_planner_agent.config import SAMPLE_TASKS_PATH, TASKS_PATH
from daily_planner_agent.models import Priority, Task, TaskCreate


class TaskStoreError(RuntimeError):
    """Raised when the local task store cannot satisfy an operation."""


class TaskNotFoundError(TaskStoreError):
    """Raised when a task ID does not exist in the task store."""


def ensure_task_store(
    path: Path = TASKS_PATH,
    sample_path: Path = SAMPLE_TASKS_PATH,
) -> None:
    if path.exists():
        return
    if not sample_path.exists():
        raise TaskStoreError(f"Sample task data not found: {sample_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample_path, path)


def load_tasks(path: Path = TASKS_PATH) -> list[Task]:
    ensure_task_store(path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TaskStoreError(f"Task store is not valid JSON: {path}") from exc

    if not isinstance(raw, list):
        raise TaskStoreError("Task store must be a JSON array.")

    try:
        return [Task.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise TaskStoreError(f"Task store schema validation failed: {exc}") from exc


def save_tasks(tasks: list[Task], path: Path = TASKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [task.model_dump(mode="json") for task in tasks]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def list_tasks(
    *,
    include_completed: bool = True,
    path: Path = TASKS_PATH,
) -> list[Task]:
    tasks = load_tasks(path)
    if include_completed:
        return tasks
    return [task for task in tasks if not task.completed]


def list_todays_tasks(
    *,
    today: date | None = None,
    path: Path = TASKS_PATH,
) -> list[Task]:
    reference_date = today or date.today()
    return [
        task
        for task in load_tasks(path)
        if not task.completed and task.due_date <= reference_date
    ]


def add_task(
    *,
    title: str,
    description: str = "",
    due_date: date | str,
    estimated_minutes: int,
    priority: Priority = "medium",
    path: Path = TASKS_PATH,
) -> Task:
    tasks = load_tasks(path)
    task_data = TaskCreate(
        title=title,
        description=description,
        due_date=due_date,
        estimated_minutes=estimated_minutes,
        priority=priority,
    )
    task = Task(id=_new_task_id(tasks), **task_data.model_dump())
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def complete_task(task_id: str, *, path: Path = TASKS_PATH) -> Task:
    tasks = load_tasks(path)
    for index, task in enumerate(tasks):
        if task.id == task_id:
            completed_task = task.model_copy(update={"completed": True})
            tasks[index] = completed_task
            save_tasks(tasks, path)
            return completed_task
    raise TaskNotFoundError(f"Task not found: {task_id}")


def reset_tasks(
    *,
    path: Path = TASKS_PATH,
    sample_path: Path = SAMPLE_TASKS_PATH,
) -> list[Task]:
    if not sample_path.exists():
        raise TaskStoreError(f"Sample task data not found: {sample_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sample_path, path)
    return load_tasks(path)


def task_to_dict(task: Task) -> dict[str, object]:
    return task.model_dump(mode="json")


def _new_task_id(existing_tasks: list[Task]) -> str:
    existing_ids = {task.id for task in existing_tasks}
    while True:
        candidate = f"task-{uuid4().hex[:8]}"
        if candidate not in existing_ids:
            return candidate
