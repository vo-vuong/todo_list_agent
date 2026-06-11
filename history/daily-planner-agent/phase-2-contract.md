# Phase Contract: Phase 2 - Agent report flow

**Feature slug:** daily-planner-agent
**Source of truth:** `history/daily-planner-agent/CONTEXT.md`
**Phase plan:** `history/daily-planner-agent/phase-plan.md`

## Entry State

Phase 1 has produced a runnable `uv` Python project with validated local JSON task data, reset behavior, and a separate FastMCP SSE server exposing `list_tasks`, `add_task`, `complete_task`, and `reset_tasks`. The MCP validation client can call those tools over `http://localhost:8000/sse`, and `data/tasks.json` can be reset to `data/tasks.sample.json`.

## Exit State

The project has a CLI-driven agent report flow that connects to the running MCP server by URL, optionally completes a task through MCP with `--complete <task_id>`, fetches today's incomplete tasks through MCP, calls OpenAI through PydanticAI using `OPENAI_MODEL` defaulting to `gpt-5-nano`, and writes a concise dated markdown report to `reports/daily-plan-YYYY-MM-DD.md`.

The flow fails clearly before LLM planning when `OPENAI_API_KEY` is missing. It enforces the fixed 09:00-17:00 local workday, blocks lunch from 12:00-13:00, and places tasks that do not fit under `Unscheduled overflow`.

## Demo / Proof

- Run `uv sync`.
- Start the MCP server with `uv run daily-planner-mcp`.
- Run the CLI without `OPENAI_API_KEY` and confirm it fails clearly before LLM planning.
- With `OPENAI_API_KEY`, run the CLI and produce `reports/daily-plan-YYYY-MM-DD.md`.
- Run the CLI with `--complete <task_id>` and confirm the task is completed through MCP before the report is generated.
- Inspect the markdown report for title/date, summary, time-block table, and `Unscheduled overflow`.

## Stories

| Story | What Happens | Unlocks | Done When |
|---|---|---|---|
| S1 | Runtime config adds OpenAI model/key settings, report paths, and a CLI entry point while keeping the MCP server URL behavior from Phase 1. | Planner and report code can share consistent settings. | `pyproject.toml`, `.env.example`, and config expose the expected Phase 2 runtime knobs. |
| S2 | The app has reusable MCP client helpers for listing today's tasks and completing a task by ID through the running SSE server. | The CLI and later Streamlit UI can call the same task actions. | A validation command proves list and complete calls go through MCP, not direct store functions. |
| S3 | The PydanticAI planner calls OpenAI with today's MCP tasks and returns a structured schedule plan respecting priorities, workday hours, lunch, and overflow. | Markdown report generation can be deterministic around a typed planning result. | Tests or validation confirm the planner refuses missing API keys and shapes successful output into the expected model. |
| S4 | Markdown rendering writes the dated report with title/date, summary, time-block table, and `Unscheduled overflow`. | CLI output becomes the proof surface for the core daily planner agent. | A generated report exists under `reports/` and contains the required sections. |
| S5 | The CLI wires optional `--complete <task_id>`, MCP task fetch, LLM planning, report writing, and user-facing status/errors. | Phase 3 can wrap a proven planner/report path in Streamlit. | CLI validation passes with and without `--complete`, and missing-key behavior is clear. |

## Boundaries

**Out:** Streamlit UI, report preview/download UI, Streamlit missing-key display, notifications, authentication, drag-and-drop scheduling, and changing the Phase 1 MCP server tool contract unless validation proves a small compatibility fix is required.
**Success:** The agent report flow is runnable from CLI, proves MCP list/complete calls, performs a real OpenAI/PydanticAI planning call when credentials exist, and writes the required markdown report.
**Pivot:** Revise the plan if the installed PydanticAI version cannot connect to the FastMCP SSE server or cannot support the required OpenAI model/provider path without changing locked decisions.
