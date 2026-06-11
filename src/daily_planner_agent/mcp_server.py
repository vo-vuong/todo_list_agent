from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from daily_planner_agent.config import get_mcp_server_settings
from daily_planner_agent.models import Priority
from daily_planner_agent.planner import generate_daily_plan
from daily_planner_agent.reporting import render_markdown_report, write_markdown_report
from daily_planner_agent.store import (
    add_task as store_add_task,
    complete_task as store_complete_task,
    list_tasks as store_list_tasks,
    list_todays_tasks,
    reset_tasks as store_reset_tasks,
    task_to_dict,
)


def create_mcp_server() -> FastMCP:
    settings = get_mcp_server_settings()
    mcp = FastMCP(
        "Daily Planner Task Store",
        host=settings.host,
        port=settings.port,
        sse_path=settings.sse_path,
        json_response=True,
    )

    @mcp.tool()
    def list_tasks(today_only: bool = False, include_completed: bool = True) -> list[dict[str, Any]]:
        """List tasks in the daily planner task store.

        Use this tool when the user asks to view tasks, inspect available work,
        find a task ID, check whether a task title is unique, or gather context
        before choosing a completion tool.

        Args:
            today_only: When true, return only incomplete tasks that are due on
                or before the current local date. Use this for daily planning.
                When false, return tasks across all due dates.
            include_completed: When true, include completed and incomplete
                tasks. When false, return only incomplete tasks.

        Returns:
            A list of task objects with id, title, description, due_date,
            estimated_minutes, priority, and completed fields.

        Side effects:
            None. This is a read-only tool.
        """
        tasks = list_todays_tasks() if today_only else store_list_tasks(include_completed=include_completed)
        return [task_to_dict(task) for task in tasks]

    @mcp.tool()
    def add_task(
        title: str,
        due_date: str,
        estimated_minutes: int,
        priority: Priority = "medium",
        description: str = "",
    ) -> dict[str, Any]:
        """Create a new task in the daily planner task store.

        Use this tool only when the user clearly wants to add or create a task
        and has provided the required task fields. Do not use it for completing
        existing tasks or generating reports.

        Args:
            title: Required task title. Preserve the user's wording.
            due_date: Required due date in YYYY-MM-DD format.
            estimated_minutes: Required positive estimate in minutes.
            priority: Task priority; must be one of low, medium, or high.
            description: Optional task description. Use an empty string when the
                user does not provide useful description text.

        Returns:
            The created task object with generated id and completed=false.

        Side effects:
            Writes the new task to data/tasks.json.
        """
        task = store_add_task(
            title=title,
            description=description,
            due_date=due_date,
            estimated_minutes=estimated_minutes,
            priority=priority,
        )
        return task_to_dict(task)

    @mcp.tool()
    def complete_task(task_id: str) -> dict[str, Any]:
        """Complete an existing task by exact task ID.

        Use this tool when the user provides a known exact task ID and asks to
        mark that task as done, completed, finished, or xong. If the user gives
        a task title instead of an ID, prefer complete_task_by_reference because
        it can resolve unique titles and report ambiguity.

        Args:
            task_id: Exact task id, such as today-medium or task-abc12345.

        Returns:
            The updated task object with completed=true.

        Side effects:
            Updates data/tasks.json by marking the matching task completed.
        """
        return task_to_dict(store_complete_task(task_id))

    @mcp.tool()
    def complete_task_by_reference(reference: str) -> dict[str, Any]:
        """Complete a task by exact task ID or by unique incomplete task title.

        Use this as the preferred completion tool for natural-language chat
        requests because users may mention either a task ID or a task title. It
        first tries exact task ID matching. If no ID matches, it tries an exact
        case-insensitive match against incomplete task titles.

        Args:
            reference: The user's task reference. Pass the exact task ID when
                present, otherwise pass the task title text from the user.

        Returns:
            A structured result:
            - status="completed" with task when the task was completed.
            - status="needs_clarification" with matches when multiple
              incomplete tasks share the title, or when reference is empty.
            - status="not_found" when no task ID or incomplete task title
              matches.

        Side effects:
            Marks one task completed only when there is an exact ID match or a
            single unique incomplete title match. It does not complete anything
            when the title is ambiguous or missing.
        """
        return complete_task_by_reference_result(reference)

    @mcp.tool()
    async def generate_daily_report() -> dict[str, Any]:
        """Generate today's daily plan markdown report file.

        Use this tool when the user asks to create, generate, export, or write a
        daily plan, plan markdown, markdown report, or today's schedule report.
        This tool gathers today's incomplete due or overdue tasks, asks the
        planner to create a DailyPlan, writes the markdown file, and returns the
        report path and markdown content.

        Args:
            None.

        Returns:
            A structured result with status="generated", message, path,
            markdown, task_count, and plan_date.

        Side effects:
            Calls the planner model and writes reports/daily-plan-YYYY-MM-DD.md.
            Requires OPENAI_API_KEY to be configured.
        """
        return await generate_daily_report_result()

    @mcp.tool()
    def reset_tasks() -> list[dict[str, Any]]:
        """Reset the task store back to the sample data.

        Use this tool only when the user explicitly asks to reset, restore, or
        reload the sample task data. Do not use it for normal task completion,
        report generation, or task lookup.

        Args:
            None.

        Returns:
            The full restored task list.

        Side effects:
            Overwrites data/tasks.json with data/tasks.sample.json.
        """
        return [task_to_dict(task) for task in store_reset_tasks()]

    return mcp


def complete_task_by_reference_result(reference: str) -> dict[str, Any]:
    normalized = reference.strip()
    if not normalized:
        return {
            "status": "needs_clarification",
            "message": "Which task should I complete?",
            "matches": [],
        }

    tasks = store_list_tasks(include_completed=True)
    for task in tasks:
        if task.id == normalized:
            completed = store_complete_task(task.id)
            return {
                "status": "completed",
                "message": f"Completed task {completed.id}.",
                "task": task_to_dict(completed),
            }

    title_matches = [
        task
        for task in tasks
        if not task.completed and task.title.casefold() == normalized.casefold()
    ]
    if len(title_matches) == 1:
        completed = store_complete_task(title_matches[0].id)
        return {
            "status": "completed",
            "message": f"Completed task {completed.id}.",
            "task": task_to_dict(completed),
        }
    if len(title_matches) > 1:
        return {
            "status": "needs_clarification",
            "message": "Multiple incomplete tasks match that title. Which task ID should I complete?",
            "matches": [task_to_dict(task) for task in title_matches],
        }

    return {
        "status": "not_found",
        "message": f"No incomplete task title or task ID matched: {normalized}",
        "matches": [],
    }


async def generate_daily_report_result() -> dict[str, Any]:
    tasks = list_todays_tasks()
    plan = await generate_daily_plan(tasks)
    path = write_markdown_report(plan)
    markdown = render_markdown_report(plan)
    return {
        "status": "generated",
        "message": f"Report written to {path}.",
        "path": str(path),
        "markdown": markdown,
        "task_count": len(tasks),
        "plan_date": plan.plan_date.isoformat(),
    }


def main() -> None:
    mcp = create_mcp_server()
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
