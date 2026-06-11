# Story Map: Phase 1 - MCP task store loop

**Feature slug:** daily-planner-agent
**Phase contract:** `history/daily-planner-agent/phase-1-contract.md`

## Dependency Diagram

Entry -> S1 scaffold -> S2 task data -> S3 store behavior -> S4 MCP server tools -> S5 README and validation -> Exit

## Story Table

| Story | Outcome | Contributes To | Creates | Done |
|---|---|---|---|---|
| S1 | The demo has a `uv` Python project and importable package. | Repeatable setup. | `pyproject.toml`, `src/daily_planner_agent/__init__.py`, initial package modules. | `uv sync` succeeds and imports work. |
| S2 | Task data exists in sample and mutable files using the locked schema. | Repeatable local store. | `data/tasks.sample.json`, `data/tasks.json`. | Files include `id`, `title`, `description`, `due_date`, `estimated_minutes`, `priority`, and `completed`. |
| S3 | Store operations handle schema validation, priority validation, today's-task filtering, add, complete, and reset. | Reliable tool implementation. | `models.py`, `store.py`, focused tests or validation commands. | Operations mutate or restore `data/tasks.json` as expected. |
| S4 | FastMCP exposes the task store through a separate HTTP/SSE server process. | Client-server MCP boundary for later phases. | `mcp_server.py`, server run command. | Server starts and tools can be invoked for list/add/complete/reset. |
| S5 | Phase 1 can be reproduced from documentation. | Handoff to Phase 2. | `README.md` updates and validation notes. | README has `uv sync`, server startup, and Phase 1 checks. |

## Story-To-Work-Plan Mapping

| Story | Work Plan Step | Proof |
|---|---|---|
| S1 | Step 1 | `uv sync` and import check. |
| S2 | Step 2 | JSON files contain valid representative tasks. |
| S3 | Step 3 | Store validation or tests prove list/add/complete/reset and today's filter. |
| S4 | Step 4 | MCP server starts and exposes the required tools. |
| S5 | Step 5 | README commands match verified commands. |
