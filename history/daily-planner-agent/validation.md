# Daily Planner Agent - Validation

**Feature slug:** daily-planner-agent
**Date:** 2026-06-11
**Mode:** standard_feature
**Current work:** Implement Phase 3: make Streamlit the primary demo interface with `Tasks` and `Planner` tabs that call the existing MCP server, planner, and report writer, while documenting and validating the final local demo flow.
**Source of truth:** `history/daily-planner-agent/CONTEXT.md`
**Plan:** `history/daily-planner-agent/work-plan.md`

## Reality Gate

| Check | Result | Evidence |
|---|---|---|
| Mode fit | PASS | `history/daily-planner-agent/phase-plan.md` defines Phase 3 as the Streamlit demo interface after MCP and planner/report flows exist; `work-plan.md` scopes current work to that UI phase. |
| Repo fit | PASS | Current repo has Phase 1 and Phase 2 foundations: `pyproject.toml`, `src/daily_planner_agent/mcp_server.py`, `mcp_client.py`, `planner.py`, `reporting.py`, `cli.py`, sample data, reports directory, and tests. |
| Assumptions | PASS | `uv --version` -> `uv 0.8.3`; `python --version` -> `Python 3.12.9`; `uv run pytest` -> 9 passed; `uvx --from streamlit streamlit --version` -> `Streamlit, version 1.58.0`. |
| Smaller path | PASS | The smallest useful current work is the full Phase 3 UI wrapper because the `Tasks` and `Planner` tabs must be validated together against the same MCP server and report flow. |
| Proof surface | PASS | Work plan includes concrete proofs: tests, Streamlit launch, MCP task actions, planner report preview/download, missing-key UI behavior, and unavailable-MCP UI behavior. |

## Feasibility Matrix

| Part / Assumption | Risk | Proof Required | Evidence | Result |
|---|---|---|---|---|
| Streamlit dependency and command are available. | LOW | Verify Streamlit can be resolved and exposes the CLI command. | `uvx --from streamlit streamlit --version` installed Streamlit and printed `Streamlit, version 1.58.0`. | PASS |
| Existing tests remain green before Phase 3 edits. | LOW | Run current test suite. | `uv run pytest` collected 9 items and passed all tests. | PASS |
| UI can reuse existing planner/report modules without hidden architecture work. | LOW | Import the current helpers expected by the UI. | `uv run python -c "... import list_todays_tasks, complete_task, generate_daily_plan, require_openai_api_key, write_markdown_report ..."` printed `imports_ok`. | PASS |
| MCP SSE boundary is still runnable for UI task actions. | LOW | Start server and call list/add/complete/reset through the real MCP client check. | Background `uv run daily-planner-mcp` opened port 8000; `uv run python -m daily_planner_agent.mcp_client_check` listed tools, returned 3 today's tasks, added `task-ab46914a`, completed it, and reset to 4 tasks. | PASS |
| UI task actions can stay behind MCP instead of direct JSON writes. | MEDIUM | Confirm server already has list/add/complete/reset tools and client has an extraction pattern. | `src/daily_planner_agent/mcp_server.py` exposes `list_tasks`, `add_task`, `complete_task`, and `reset_tasks`; `src/daily_planner_agent/mcp_client.py` already calls MCP and validates payloads into `Task`. | PASS |
| Missing-key behavior can be shown in UI before LLM planning. | LOW | Confirm Phase 2 planner exposes a clear guard. | `src/daily_planner_agent/planner.py` has `require_openai_api_key()` raising `MissingOpenAIKeyError` with a clear message before constructing the OpenAI model. | PASS |
| Report preview/download can use deterministic markdown. | LOW | Confirm report renderer/writer already exists. | `src/daily_planner_agent/reporting.py` provides `render_markdown_report()` and `write_markdown_report()` with title/date, summary, time-block table, and overflow sections. | PASS |
| Async MCP/planner helpers can be called from Streamlit. | MEDIUM | Validate that async helpers are isolated and can be wrapped synchronously. | Existing CLI uses `anyio.run()` in `src/daily_planner_agent/cli.py`; Phase 3 can reuse the same pattern in UI action wrapper functions. | PASS WITH CONSTRAINT |
| Full planner UI validation can make a real OpenAI call. | MEDIUM | Confirm validation can require live key at implementation time without automated tests depending on it. | Phase 2 execution log and review recorded real-key CLI report generation; current work plan explicitly keeps automated tests non-LLM and requires manual real-key UI validation. | PASS WITH CONSTRAINT |
| Existing Phase 2 P2 finding does not block UI implementation. | MEDIUM | Ensure the finding is known and constrained. | `history/daily-planner-agent/review.md` records a P2 about post-LLM task membership/priority validation. It is non-blocking but must not be hidden by the UI; implementation may fix it if touching planner validation. | PASS WITH CONSTRAINT |

## Probes

- `uv --version`: PASS, local `uv` is installed.
- `python --version`: PASS, Python 3.12.9 is available from shell.
- `uv run pytest`: PASS, 9 tests passed.
- `uvx --from streamlit streamlit --version`: PASS, Streamlit CLI is available through `uv`.
- Import probe: PASS, current MCP/planner/report helpers import successfully.
- MCP server/client check: PASS, real SSE flow listed, added, completed, and reset tasks.

## Integration Readiness

- Phase 3 can be wired without hidden architecture work: task storage and mutation already sit behind FastMCP SSE tools, and planner/report generation already exists as importable Python functions.
- `mcp_client.py` needs only small expansion for UI workflows that Phase 2 did not require: list all tasks, add task, and reset tasks.
- `streamlit_app.py` can keep all UI actions behind MCP client helpers, preserving D8 and D16.
- Missing-key UI behavior can call or catch the existing `require_openai_api_key()` / `MissingOpenAIKeyError` path.
- README can move from a Phase 2 CLI description to a final two-process Streamlit demo without changing the already working CLI path.

## Verification Readiness

- `uv sync`
- `uv run pytest`
- Start server: `uv run daily-planner-mcp`
- Start UI with the documented Streamlit command.
- In `Tasks`, list tasks, add a task, complete a selected task, and reset sample data.
- In `Planner`, with `OPENAI_API_KEY` set, generate and preview/download `reports/daily-plan-YYYY-MM-DD.md`.
- With `OPENAI_API_KEY` empty or absent, verify the Planner tab shows a clear error and does not generate an LLM plan.
- Stop or avoid starting the MCP server and verify the UI reports the MCP connection problem clearly.

## Decision

READY WITH CONSTRAINTS

## Constraints For Implementation

- Do not bypass MCP in Streamlit task actions; listing, adding, completing, and resetting tasks must go through MCP client helpers.
- Keep the UI exactly split into `Tasks` and `Planner` tabs.
- Use the existing PydanticAI planner and deterministic report writer instead of adding a second planning/report path.
- Add Streamlit through `pyproject.toml` and document `uv run ...` commands.
- Keep automated tests free of real OpenAI calls; reserve real-key planner verification for manual implementation validation.
- Surface missing `OPENAI_API_KEY` and unavailable MCP server errors clearly in the UI.
- Preserve existing CLI behavior and tests while adding the UI.
- Track the Phase 2 P2 planner-output membership/priority finding; do not make the UI imply stronger validation than the planner currently enforces unless the implementation fixes it.

## Approval

Execution approved: yes
Implementation may start only after this changes to yes in conversation and
`.khuym/state.json` has `approved_gates.execution = true`.
