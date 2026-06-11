from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client
from pydantic import BaseModel, ConfigDict

from daily_planner_agent.config import get_mcp_server_settings
from daily_planner_agent.models import Priority, Task


class McpClientError(RuntimeError):
    """Raised when the planner cannot call the MCP task server."""


class McpToolInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""


@asynccontextmanager
async def task_session() -> AsyncIterator[ClientSession]:
    settings = get_mcp_server_settings()
    async with AsyncExitStack() as stack:
        try:
            read_stream, write_stream = await stack.enter_async_context(sse_client(settings.url))
            session = await stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()
        except Exception as exc:
            raise McpClientError(f"Could not connect to MCP server at {settings.url}") from exc
        yield session


async def discover_tools() -> list[McpToolInfo]:
    async with task_session() as session:
        result = await session.list_tools()
    return [
        McpToolInfo(
            name=tool.name,
            description=tool.description or "",
        )
        for tool in result.tools
    ]


async def list_tasks(*, include_completed: bool = True) -> list[Task]:
    async with task_session() as session:
        result = await session.call_tool(
            "list_tasks",
            {"today_only": False, "include_completed": include_completed},
        )
    return [Task.model_validate(item) for item in _extract_items(result)]


async def list_todays_tasks() -> list[Task]:
    async with task_session() as session:
        result = await session.call_tool("list_tasks", {"today_only": True})
    return [Task.model_validate(item) for item in _extract_items(result)]


async def complete_task(task_id: str) -> Task:
    async with task_session() as session:
        result = await session.call_tool("complete_task", {"task_id": task_id})
    return Task.model_validate(_extract_item(result))


async def add_task(
    *,
    title: str,
    due_date: str,
    estimated_minutes: int,
    priority: Priority = "medium",
    description: str = "",
) -> Task:
    async with task_session() as session:
        result = await session.call_tool(
            "add_task",
            {
                "title": title,
                "description": description,
                "due_date": due_date,
                "estimated_minutes": estimated_minutes,
                "priority": priority,
            },
        )
    return Task.model_validate(_extract_item(result))


async def reset_tasks() -> list[Task]:
    async with task_session() as session:
        result = await session.call_tool("reset_tasks", {})
    return [Task.model_validate(item) for item in _extract_items(result)]


def _extract_items(result: object) -> list[dict[str, Any]]:
    content = getattr(result, "structuredContent", None)
    if isinstance(content, list):
        return [_ensure_dict(item) for item in content]
    if isinstance(content, dict):
        if isinstance(content.get("result"), list):
            return [_ensure_dict(item) for item in content["result"]]
        if isinstance(content.get("items"), list):
            return [_ensure_dict(item) for item in content["items"]]
    raise McpClientError("MCP tool did not return a task list.")


def _extract_item(result: object) -> dict[str, Any]:
    content = getattr(result, "structuredContent", None)
    if isinstance(content, dict):
        if isinstance(content.get("result"), dict):
            return _ensure_dict(content["result"])
        return _ensure_dict(content)
    raise McpClientError("MCP tool did not return a task object.")


def _ensure_dict(item: object) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise McpClientError("MCP task payload must be a JSON object.")
    return item
