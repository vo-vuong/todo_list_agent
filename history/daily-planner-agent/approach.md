# Daily Planner Agent - Approach

**Feature slug:** daily-planner-agent
**Date:** 2026-06-10
**Source of truth:** `history/daily-planner-agent/CONTEXT.md`

## Repo Reality

- `history/daily-planner-agent/CONTEXT.md` - Approved source of truth with 16 locked decisions covering Python, PydanticAI, FastMCP, SSE topology, Streamlit UI, JSON task store, report format, and `uv` workflow.
- `.env.example` - Already exists with `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-5-nano`, and `MCP_SERVER_URL=http://localhost:8000/sse`, matching the required configuration direction.
- Project root - No `pyproject.toml`, `src/`, `data/`, `reports/`, tests, README, or implementation files exist yet, so this work starts as a new Python application scaffold.
- Repository metadata - This directory is not currently a git repository, so validation cannot rely on git diff and must rely on generated artifacts, commands, and manual checks.

## Chosen Mode And Shape

**Mode:** `standard_feature`
**Shape:** `phase-plan`

Why this is the least workflow that protects the work:

The feature needs multiple observable capabilities in order: MCP-backed task mutations, LLM planning/report generation, then Streamlit workflows.

Why smaller shapes are insufficient, if above `small_change`:

`direct_task`, `spike`, and `small_change` are too small because the locked scope spans runtime scaffolding, a separate MCP server process, a PydanticAI client, Streamlit UI states, markdown export, reset behavior, and credential error handling.

## Decision Coverage

| Decision | Planning Impact | Covered By |
|---|---|---|
| D1 | Requires a real OpenAI-backed agent while keeping the task store behind MCP. | Phase 2, Phase 3 |
| D2 | Defines the task model and JSON storage contract. | Phase 1 |
| D3 | Limits output to a dated markdown report. | Phase 2, Phase 3 |
| D4 | Requires a CLI `--complete <task_id>` path before planning. | Phase 2 |
| D5 | Makes Streamlit the primary interface. | Phase 3 |
| D6 | Requires PydanticAI for the agent layer. | Phase 2 |
| D7 | Requires official MCP Python SDK FastMCP import style. | Phase 1 |
| D8 | Requires a separate HTTP/SSE MCP server process and URL-based client connection. | Phase 1, Phase 2, Phase 3 |
| D9 | Requires `.env` config, `gpt-5-nano` default, and clear missing-key UI behavior. | Phase 2, Phase 3 |
| D10 | Defines the "today's tasks" filter. | Phase 1, Phase 2 |
| D11 | Defines workday, lunch, and overflow scheduling constraints. | Phase 2 |
| D12 | Restricts stored priority values and prevents the LLM from mutating priority. | Phase 1, Phase 2, Phase 3 |
| D13 | Defines concise markdown report sections. | Phase 2 |
| D14 | Defines the Streamlit two-tab UI. | Phase 3 |
| D15 | Requires `uv`, `pyproject.toml`, and `uv run` instructions. | Phase 1, Phase 3 |
| D16 | Requires sample data and reset behavior that restores it. | Phase 1, Phase 3 |

## Approach

Build the project in observable phases. Start by making the task store usable through a real FastMCP SSE server with deterministic local data, because every later agent and UI workflow depends on that boundary. Then add the PydanticAI planner and CLI report flow, including the real OpenAI call, `--complete`, date filtering, workday constraints, and markdown export. Finish with the Streamlit primary interface, wiring the same MCP and planner paths into tabs that expose task operations, planning, preview/download, reset, and missing-key errors.

## Likely Files

- `pyproject.toml` - `uv` project metadata, dependencies, scripts, and Python version.
- `README.md` - Setup, two-process run commands, CLI examples, Streamlit run instructions, and validation flow.
- `.env.example` - Existing configuration example; may need small alignment with final command names.
- `data/tasks.sample.json` - Immutable sample task data used by reset behavior.
- `data/tasks.json` - Mutable local JSON task store used by MCP tools and demo workflows.
- `reports/.gitkeep` - Keeps the generated report directory present without committing generated reports.
- `src/daily_planner_agent/config.py` - `.env` loading and runtime settings.
- `src/daily_planner_agent/models.py` - Task and planner data models.
- `src/daily_planner_agent/store.py` - JSON read/write, validation, task filtering, and reset logic.
- `src/daily_planner_agent/mcp_server.py` - FastMCP server exposing `list_tasks`, `add_task`, `complete_task`, and reset support.
- `src/daily_planner_agent/planner.py` - PydanticAI agent connection to the MCP server and schedule generation.
- `src/daily_planner_agent/reporting.py` - Markdown report rendering and dated file writing.
- `src/daily_planner_agent/cli.py` - CLI entry point including `--complete <task_id>` and report generation.
- `src/daily_planner_agent/streamlit_app.py` - Two-tab Streamlit UI.
- `tests/` - Focused tests for store behavior, today's-task filtering, report formatting, and missing-key guards where feasible.

## Risks

- PydanticAI MCP connection details and FastMCP SSE startup behavior need current package-level verification during validation before code edits.
- A real OpenAI call is required for full planner validation, so local verification depends on `OPENAI_API_KEY` being present.
- Generated LLM text can vary, so validation should check required markdown structure and scheduling constraints rather than exact prose.
- The separate server process means UI and CLI validation must include clear failure behavior when `MCP_SERVER_URL` is unavailable.

## Validation Needs

- `uv sync`
- Start the MCP server with a documented `uv run ...` command.
- Use the app or a small command to prove `list_tasks`, `add_task`, `complete_task`, and reset mutate `data/tasks.json` correctly.
- Run the CLI with `--complete <task_id>` and confirm it completes the task before generating `reports/daily-plan-YYYY-MM-DD.md`.
- Run Streamlit and manually verify the `Tasks` and `Planner` tabs.
- Verify missing `OPENAI_API_KEY` shows a clear Streamlit error and does not generate an LLM plan.

## Handoff

Use this approach plus the selected shape artifact before editing code. Do not
expand scope beyond `CONTEXT.md` without returning to clarification.
