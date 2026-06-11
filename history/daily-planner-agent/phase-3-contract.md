# Phase Contract: Phase 3 - Streamlit Demo Interface

**Feature slug:** daily-planner-agent
**Source of truth:** `history/daily-planner-agent/CONTEXT.md`
**Phase plan:** `history/daily-planner-agent/phase-plan.md`

## Entry State

Phase 1 and Phase 2 are implemented and reviewed. The project already has a `uv` Python scaffold, local JSON task store, resettable sample data, FastMCP SSE server tools, MCP client helpers, PydanticAI/OpenAI planner, CLI `--complete` report flow, markdown report writer, README CLI/server instructions, and tests passing. Streamlit is still deferred, and the README still describes Phase 2 as the current demo.

## Exit State

The demo has a Streamlit primary interface with two tabs:

- `Tasks` lists current tasks through the MCP server, adds tasks, completes a selected task, and resets sample data.
- `Planner` generates the LLM daily plan through the existing planner/report path, previews the markdown report, and exposes a download action.

The UI loads `.env` settings, connects to the separate MCP SSE server by URL, shows a clear missing `OPENAI_API_KEY` error before LLM planning, handles unavailable MCP server errors clearly, and uses `uv run` instructions in README. The project dependencies and scripts include Streamlit. Existing CLI and MCP behavior remain working.

## Demo / Proof

- Start the MCP server with `uv run daily-planner-mcp`.
- Start the UI with the documented `uv run ...` Streamlit command.
- In the `Tasks` tab, list tasks, add a task, complete a selected task, and reset sample data.
- In the `Planner` tab, generate a plan with `OPENAI_API_KEY` set, preview the markdown, and download the dated report.
- Clear `OPENAI_API_KEY` and verify the UI shows an explicit error without generating an LLM plan.
- Run `uv run pytest`.

## Stories

| Story | What Happens | Unlocks | Done When |
|---|---|---|---|
| S1 | Add Streamlit dependency, entry point, and UI shell with the required two tabs. | Task and planner workflows can be exposed in one primary interface. | `uv` can launch the Streamlit app and it renders `Tasks` and `Planner` tabs. |
| S2 | Wire the `Tasks` tab to MCP task operations for listing, adding, completing selected tasks, and reset. | The UI proves task store mutation through the same separate MCP boundary as the CLI. | Each task action updates `data/tasks.json` through MCP and refreshes visible task state. |
| S3 | Wire the `Planner` tab to existing missing-key guard, planner, report writer, preview, and download behavior. | The primary UI proves the end-to-end daily planner output. | With a key, a dated markdown report is written and previewed; without a key, planning is blocked with a clear error. |
| S4 | Update README and focused tests for the Streamlit-facing helpers and final run flow. | The full demo is repeatable and reviewable. | README documents setup/server/UI/validation, and tests cover non-LLM helper behavior without requiring a real key. |

## Boundaries

**Out:** Authentication, multi-user support, drag-and-drop scheduling, browser persistence, notification output, embedded single-process MCP, and visual redesign beyond a small functional Streamlit demo.
**Success:** The UI is the primary runnable demo and covers the locked task and planner workflows without regressing CLI/MCP behavior.
**Pivot:** If Streamlit cannot call async MCP helpers reliably without brittle event-loop workarounds, isolate synchronous wrapper functions before expanding UI behavior.
