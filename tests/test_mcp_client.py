from __future__ import annotations

from daily_planner_agent.mcp_client import _extract_items


class Result:
    def __init__(self, structured_content: object) -> None:
        self.structuredContent = structured_content


def test_extract_items_accepts_mcp_items_wrapper() -> None:
    items = _extract_items(Result({"items": [{"id": "task-1"}]}))

    assert items == [{"id": "task-1"}]
