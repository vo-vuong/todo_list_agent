from __future__ import annotations

from collections.abc import Awaitable
from datetime import date
from pathlib import Path
from typing import TypeVar, cast

import anyio
import streamlit as st

from daily_planner_agent.chat_agent import ChatMessage, ChatRole, draft_task_from_chat
from daily_planner_agent.config import get_mcp_server_settings
from daily_planner_agent.mcp_client import (
    McpClientError,
    add_task,
    complete_task,
    list_tasks,
    list_todays_tasks,
    reset_tasks,
)
from daily_planner_agent.models import DailyPlan, Priority, Task, TaskCreate
from daily_planner_agent.planner import MissingOpenAIKeyError, generate_daily_plan, require_openai_api_key
from daily_planner_agent.reporting import render_markdown_report, write_markdown_report

T = TypeVar("T")
CHAT_MESSAGES_KEY = "chat_task_messages"
CHAT_DRAFT_KEY = "chat_task_draft"


class GeneratedReport:
    def __init__(self, *, plan: DailyPlan, markdown: str, path: Path) -> None:
        self.plan = plan
        self.markdown = markdown
        self.path = path


def main() -> None:
    st.set_page_config(page_title="Daily Planner Agent", page_icon="DP", layout="wide")
    st.title("Daily Planner Agent")
    st.caption(f"MCP server: {get_mcp_server_settings().url}")

    tasks_tab, planner_tab, chat_tab = st.tabs(["Tasks", "Planner", "Chat"])
    with tasks_tab:
        render_tasks_tab()
    with planner_tab:
        render_planner_tab()
    with chat_tab:
        render_chat_tab()


def render_tasks_tab() -> None:
    tasks = _load_tasks_for_ui()
    _render_task_table(tasks)
    _render_add_task_form()
    _render_complete_task_control(tasks)
    _render_reset_control()


def render_planner_tab() -> None:
    if st.button("Generate daily plan", type="primary"):
        try:
            require_openai_api_key()
            report = run_async(_generate_report())
        except MissingOpenAIKeyError as exc:
            st.error(str(exc))
        except McpClientError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not generate the daily plan: {exc}")
        else:
            st.session_state["latest_report_markdown"] = report.markdown
            st.session_state["latest_report_path"] = str(report.path)
            st.success(f"Report written to {report.path}")

    markdown = st.session_state.get("latest_report_markdown")
    report_path = st.session_state.get("latest_report_path")
    if markdown:
        st.markdown(markdown)
        filename = Path(report_path).name if report_path else f"daily-plan-{date.today().isoformat()}.md"
        st.download_button(
            "Download markdown",
            data=markdown,
            file_name=filename,
            mime="text/markdown",
        )


def render_chat_tab() -> None:
    _ensure_chat_state()

    for message in _chat_messages():
        with st.chat_message(message.role):
            st.markdown(message.content)

    draft = st.session_state.get(CHAT_DRAFT_KEY)
    if isinstance(draft, TaskCreate):
        _render_chat_draft(draft)

    if prompt := st.chat_input("Describe a task to create"):
        _append_chat_message("user", prompt)
        try:
            result = run_async(draft_task_from_chat(_chat_messages()))
        except MissingOpenAIKeyError as exc:
            _append_chat_message("assistant", str(exc))
        except Exception as exc:
            _append_chat_message("assistant", f"Could not draft a task: {exc}")
        else:
            if result.draft:
                st.session_state[CHAT_DRAFT_KEY] = result.draft.to_task_create()
                _append_chat_message("assistant", "I drafted a task. Review it before saving.")
            else:
                st.session_state.pop(CHAT_DRAFT_KEY, None)
                _append_chat_message("assistant", result.follow_up_question or "What details should I use for this task?")
        st.rerun()


def _render_chat_draft(draft: TaskCreate) -> None:
    st.subheader("Task draft")
    st.dataframe(task_create_rows(draft), hide_index=True, width="stretch")
    save_col, discard_col = st.columns(2)
    with save_col:
        if st.button("Save task", type="primary"):
            _save_chat_draft(draft)
    with discard_col:
        if st.button("Discard draft"):
            st.session_state.pop(CHAT_DRAFT_KEY, None)
            _append_chat_message("assistant", "Draft discarded.")
            st.rerun()


def _save_chat_draft(draft: TaskCreate) -> None:
    try:
        task = run_async(
            add_task(
                title=draft.title,
                description=draft.description,
                due_date=draft.due_date.isoformat(),
                estimated_minutes=draft.estimated_minutes,
                priority=cast(Priority, draft.priority),
            )
        )
    except McpClientError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not save task: {exc}")
    else:
        st.session_state.pop(CHAT_DRAFT_KEY, None)
        _append_chat_message("assistant", f"Saved task {task.id}.")
        st.rerun()


def run_async(awaitable: Awaitable[T]) -> T:
    return anyio.run(lambda: awaitable)


def task_rows(tasks: list[Task]) -> list[dict[str, object]]:
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat(),
            "estimated_minutes": task.estimated_minutes,
            "priority": task.priority,
            "completed": task.completed,
        }
        for task in tasks
    ]


def task_create_rows(task: TaskCreate) -> list[dict[str, object]]:
    return [
        {
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat(),
            "estimated_minutes": task.estimated_minutes,
            "priority": task.priority,
        }
    ]


def incomplete_task_options(tasks: list[Task]) -> dict[str, str]:
    return {
        f"{task.title} ({task.id})": task.id
        for task in tasks
        if not task.completed
    }


def _ensure_chat_state() -> None:
    st.session_state.setdefault(CHAT_MESSAGES_KEY, [])


def _chat_messages() -> list[ChatMessage]:
    _ensure_chat_state()
    messages: list[ChatMessage] = []
    for item in st.session_state[CHAT_MESSAGES_KEY]:
        messages.append(ChatMessage.model_validate(item))
    return messages


def _append_chat_message(role: ChatRole, content: str) -> None:
    _ensure_chat_state()
    message = ChatMessage(role=role, content=content)
    st.session_state[CHAT_MESSAGES_KEY].append(message.model_dump())


def _load_tasks_for_ui() -> list[Task]:
    try:
        return run_async(list_tasks())
    except McpClientError as exc:
        st.error(str(exc))
        return []


def _render_task_table(tasks: list[Task]) -> None:
    if tasks:
        st.dataframe(task_rows(tasks), hide_index=True, width="stretch")
    else:
        st.info("No tasks available.")


def _render_add_task_form() -> None:
    with st.form("add-task", clear_on_submit=True):
        title = st.text_input("Title")
        description = st.text_area("Description", height=80)
        due_date = st.date_input("Due date", value=date.today())
        estimated_minutes = st.number_input("Estimated minutes", min_value=1, value=30, step=5)
        priority = st.selectbox("Priority", ["medium", "high", "low"])
        submitted = st.form_submit_button("Add task")

    if not submitted:
        return
    if not title.strip():
        st.error("Task title is required.")
        return

    try:
        task = run_async(
            add_task(
                title=title.strip(),
                description=description.strip(),
                due_date=due_date.isoformat(),
                estimated_minutes=int(estimated_minutes),
                priority=cast(Priority, priority),
            )
        )
    except McpClientError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Could not add task: {exc}")
    else:
        st.success(f"Added task {task.id}")
        st.rerun()


def _render_complete_task_control(tasks: list[Task]) -> None:
    options = incomplete_task_options(tasks)
    if not options:
        st.info("No incomplete tasks to complete.")
        return

    selected = st.selectbox("Task to complete", list(options))
    if st.button("Complete selected task"):
        try:
            task = run_async(complete_task(options[selected]))
        except McpClientError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not complete task: {exc}")
        else:
            st.success(f"Completed task {task.id}")
            st.rerun()


def _render_reset_control() -> None:
    if st.button("Reset sample data"):
        try:
            tasks = run_async(reset_tasks())
        except McpClientError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not reset sample data: {exc}")
        else:
            st.success(f"Reset {len(tasks)} tasks")
            st.rerun()


async def _generate_report() -> GeneratedReport:
    tasks = await list_todays_tasks()
    plan = await generate_daily_plan(tasks)
    path = write_markdown_report(plan)
    return GeneratedReport(
        plan=plan,
        markdown=render_markdown_report(plan),
        path=path,
    )


if __name__ == "__main__":
    main()
