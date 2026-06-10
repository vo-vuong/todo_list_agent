from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from daily_planner_agent.config import get_mcp_server_settings
from daily_planner_agent.models import Priority
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
        """List tasks from the local JSON store."""
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
        """Add a task to the local JSON store."""
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
        """Mark a task as completed in the local JSON store."""
        return task_to_dict(store_complete_task(task_id))

    @mcp.tool()
    def reset_tasks() -> list[dict[str, Any]]:
        """Restore data/tasks.json from data/tasks.sample.json."""
        return [task_to_dict(task) for task in store_reset_tasks()]

    return mcp


def main() -> None:
    mcp = create_mcp_server()
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
