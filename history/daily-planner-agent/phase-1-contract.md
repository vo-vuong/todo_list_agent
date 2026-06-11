# Phase Contract: Phase 1 - MCP task store loop

**Feature slug:** daily-planner-agent
**Source of truth:** `history/daily-planner-agent/CONTEXT.md`
**Phase plan:** `history/daily-planner-agent/phase-plan.md`

## Entry State

The project has an approved context, approach, and phase plan, plus an existing `.env.example`. There is no Python project scaffold, task data, task store implementation, MCP server, README run flow, or validation harness yet.

## Exit State

The repo has a runnable `uv` Python project with local task data, validated task models, JSON store operations, reset behavior, and a separate FastMCP HTTP/SSE server exposing task listing, adding, completing, and reset tools. Phase 1 ends when those local operations can be validated without invoking OpenAI, PydanticAI planning, markdown report generation, or Streamlit.

## Demo / Proof

- Run `uv sync`.
- Start the MCP server with the documented `uv run ...` command.
- Prove the task store can list incomplete tasks due on or before the local date.
- Prove adding a task mutates `data/tasks.json`.
- Prove completing a task flips `completed` for the selected ID.
- Prove reset restores `data/tasks.json` from `data/tasks.sample.json`.

## Stories

| Story | What Happens | Unlocks | Done When |
|---|---|---|---|
| S1 | A `uv` Python scaffold and package layout are created for the demo. | Shared import paths and repeatable setup. | `uv sync` succeeds and package modules can be imported. |
| S2 | Sample and mutable task JSON files are created with the locked schema and valid priority values. | Store and MCP tools can operate on deterministic data. | `data/tasks.sample.json` and `data/tasks.json` contain representative valid tasks. |
| S3 | Task models and store functions enforce schema, priority values, today's-task filtering, add, complete, and reset behavior. | MCP tools can delegate to tested local behavior. | Local validation proves read/write/reset behavior and due-date filtering. |
| S4 | A FastMCP server exposes task-store tools over the required separate HTTP/SSE process. | Later agent and UI phases can connect by URL. | The server starts and the exposed tools can be invoked against `data/tasks.json`. |
| S5 | README instructions document setup, server startup, and Phase 1 validation. | Later phases inherit a clear run baseline. | A reader can reproduce Phase 1 without guessing commands. |

## Boundaries

**Out:** PydanticAI agent orchestration, real OpenAI calls, markdown report generation, CLI `--complete <task_id>` planning flow, and Streamlit UI.
**Success:** The MCP task store loop is runnable and repeatable with `uv`, sample data, reset behavior, and tool-level validation.
**Pivot:** Revise the plan if the official MCP Python SDK cannot serve the required HTTP/SSE topology with FastMCP in the installed version.
