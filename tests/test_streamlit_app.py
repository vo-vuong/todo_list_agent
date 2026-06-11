from __future__ import annotations

from datetime import date

from daily_planner_agent.chat_agent import ChatActionTrace, ChatToolCallTrace
from daily_planner_agent.models import Task, TaskCreate
from daily_planner_agent.streamlit_app import action_trace_rows, incomplete_task_options, task_create_rows, task_rows


def test_task_rows_uses_locked_task_schema() -> None:
    task = Task(
        id="today-medium",
        title="Review requirements",
        description="Demo task",
        due_date=date(2026, 6, 11),
        estimated_minutes=45,
        priority="medium",
        completed=False,
    )

    assert task_rows([task]) == [
        {
            "id": "today-medium",
            "title": "Review requirements",
            "description": "Demo task",
            "due_date": "2026-06-11",
            "estimated_minutes": 45,
            "priority": "medium",
            "completed": False,
        }
    ]


def test_incomplete_task_options_excludes_completed_tasks() -> None:
    tasks = [
        Task(
            id="open-task",
            title="Open task",
            due_date=date(2026, 6, 11),
            estimated_minutes=30,
            priority="high",
            completed=False,
        ),
        Task(
            id="done-task",
            title="Done task",
            due_date=date(2026, 6, 11),
            estimated_minutes=30,
            priority="low",
            completed=True,
        ),
    ]

    assert incomplete_task_options(tasks) == {"Open task (open-task)": "open-task"}


def test_task_create_rows_formats_chat_draft() -> None:
    task = TaskCreate(
        title="Prepare slides",
        description="Draft the review deck",
        due_date=date(2026, 6, 12),
        estimated_minutes=45,
        priority="high",
    )

    assert task_create_rows(task) == [
        {
            "title": "Prepare slides",
            "description": "Draft the review deck",
            "due_date": "2026-06-12",
            "estimated_minutes": 45,
            "priority": "high",
        }
    ]


def test_action_trace_rows_exposes_discovery_selection_arguments_and_summary() -> None:
    trace = ChatActionTrace(
        discovered_tools=["list_tasks", "complete_task_by_reference"],
        calls=[
            ChatToolCallTrace(
                tool_name="complete_task_by_reference",
                arguments={"reference": "Open task"},
                result_summary="completed: Completed task open-task.",
            )
        ],
    )

    assert action_trace_rows(trace) == [
        {
            "discovered_tools": "list_tasks, complete_task_by_reference",
            "selected_tool": "complete_task_by_reference",
            "arguments": {"reference": "Open task"},
            "result_summary": "completed: Completed task open-task.",
        }
    ]
