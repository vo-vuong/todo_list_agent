from __future__ import annotations

import anyio

from mcp import ClientSession
from mcp.client.sse import sse_client

from daily_planner_agent.config import get_mcp_server_settings


async def _run_check() -> None:
    settings = get_mcp_server_settings()
    async with sse_client(settings.url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print(f"tools={','.join(tool_names)}")

            listed = await session.call_tool("list_tasks", {"today_only": True})
            print(f"list_tasks_today_items={_structured_len(listed)}")

            added = await session.call_tool(
                "add_task",
                {
                    "title": "MCP validation task",
                    "description": "Created by the Phase 1 validation client.",
                    "due_date": "2026-06-10",
                    "estimated_minutes": 20,
                    "priority": "medium",
                },
            )
            task_id = added.structuredContent["id"]
            print(f"added_task_id={task_id}")

            completed = await session.call_tool("complete_task", {"task_id": task_id})
            print(f"completed_task={completed.structuredContent['completed']}")

            reset = await session.call_tool("reset_tasks", {})
            print(f"reset_task_count={_structured_len(reset)}")


def _structured_len(result: object) -> int:
    content = getattr(result, "structuredContent", None)
    if isinstance(content, list):
        return len(content)
    if isinstance(content, dict) and "result" in content and isinstance(content["result"], list):
        return len(content["result"])
    return 0


def main() -> None:
    anyio.run(_run_check)


if __name__ == "__main__":
    main()
