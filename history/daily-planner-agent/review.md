# Daily Planner Agent - Review

**Feature slug:** daily-planner-agent
**Date:** 2026-06-11
**Current work:** Implement the Phase 2 CLI agent report flow through MCP, PydanticAI/OpenAI planning, and dated markdown report export.
**Execution log:** `history/daily-planner-agent/execution-log.md`

## Summary

- P1: 0
- P2: 1
- P3: 1
- Review decision: PASS WITH NON-BLOCKING FINDINGS

## Findings

| Severity | Area | File / Line | Finding | Smallest Fix |
|---|---|---|---|---|
| P2 | reliability | `src/daily_planner_agent/planner.py:21` | The planner prompt tells the LLM to use only input tasks and preserve priority values, but the returned `DailyPlan` is accepted directly at `src/daily_planner_agent/planner.py:46` without checking task IDs or priorities against the MCP task input. `DailyPlan` validates shape/time constraints, but not membership or priority preservation, so a validly shaped LLM response could invent a task or report the wrong priority. | After `agent.run`, compare every scheduled and overflow item against a `{task.id: task.priority}` map from the input tasks. Reject or retry if an ID is unknown or a priority differs. Add tests for invented task IDs and modified priorities. |
| P3 | error-handling | `src/daily_planner_agent/mcp_client.py:18` | `task_session()` wraps all exceptions raised inside the yielded session as `Could not connect to MCP server...`. A server-side tool error, such as an invalid `--complete` task ID, can be reported as a connection failure, which makes CLI troubleshooting less precise. | Narrow the connection wrapper or translate tool-call failures separately so invalid task IDs and server errors produce accurate CLI messages. |

## Artifact Verification

| Artifact / Behavior | EXISTS | SUBSTANTIVE | WIRED | Evidence |
|---|---|---|---|---|
| Phase 2 dependency and CLI entry point | yes | yes | yes | `pyproject.toml:10` adds `pydantic-ai-slim[openai]`; `pyproject.toml:16` wires `daily-planner-plan`. |
| OpenAI settings and report path helpers | yes | yes | yes | `src/daily_planner_agent/config.py:16` defaults `gpt-5-nano`; `config.py:47` loads `OPENAI_API_KEY`; `config.py:56` builds dated report paths. |
| MCP SSE client helpers | yes | yes | yes | `src/daily_planner_agent/mcp_client.py:30` calls `list_tasks` with `today_only=True`; `mcp_client.py:36` calls `complete_task`; live MCP smoke test passed. |
| PydanticAI/OpenAI planner | yes | yes | yes | `src/daily_planner_agent/planner.py:36` constructs `OpenAIResponsesModel`; `planner.py:40` creates a typed `Agent`; real-key execution log generated a report. |
| Missing-key guard | yes | yes | yes | `src/daily_planner_agent/planner.py:50` raises `MissingOpenAIKeyError`; CLI missing-key check exited with clear error before MCP access. |
| Schedule constraints | yes | yes | yes | `src/daily_planner_agent/models.py:67` validates 09:00-17:00, lunch exclusion, and no overlapping blocks; `tests/test_reporting.py:43` covers lunch rejection. |
| Markdown report rendering and writing | yes | yes | yes | `src/daily_planner_agent/reporting.py:10` renders required sections; `reporting.py:46` writes the dated file; `reports/daily-plan-2026-06-11.md` exists from validation. |
| CLI `--complete` orchestration | yes | yes | yes | `src/daily_planner_agent/cli.py:14` completes through MCP before listing/planning; `tests/test_cli.py:11` verifies call order. |
| README Phase 2 run flow | yes | yes | yes | `README.md:40` documents plan generation; `README.md:54` documents `--complete`; `README.md:66` documents missing-key behavior. |

## Decision Coverage

| Decision | Evidence | Result |
|---|---|---|
| D1 | `planner.py` calls OpenAI through PydanticAI while `cli.py` gets task data through MCP helpers. | PASS |
| D2 | Planner input remains `Task` objects with locked fields from `models.py`. | PASS |
| D3 | `reporting.py:47` writes `reports/daily-plan-YYYY-MM-DD.md`. | PASS |
| D4 | `cli.py:14` wires `--complete` completion before planning. | PASS |
| D5 | Streamlit remains deferred; no Streamlit implementation was added in Phase 2. | PASS |
| D6 | `planner.py:5` uses `pydantic_ai.Agent` with OpenAI model/provider imports. | PASS |
| D7 | Existing FastMCP server implementation was not replaced. | PASS |
| D8 | `mcp_client.py:22` connects to the configured SSE URL; live smoke test passed. | PASS |
| D9 | `config.py:16` preserves default `gpt-5-nano`; missing-key CLI check produced the expected clear error. | PASS |
| D10 | `mcp_client.py:32` calls `list_tasks` with `today_only=True`. | PASS |
| D11 | `models.py:67` validates workday, lunch, and overlap constraints. | PASS |
| D12 | Store mutation is limited to MCP completion, but planner output does not yet enforce task membership/priority preservation after the LLM response. | PASS WITH P2 |
| D13 | `reporting.py:10` renders title/date, summary, time-block table, and `Unscheduled overflow`. | PASS |
| D14 | Streamlit two-tab UI remains deferred to Phase 3. | PASS |
| D15 | `README.md:20`, `README.md:50`, and `README.md:78` use `uv` commands. | PASS |
| D16 | MCP smoke test reset the data; post-check printed `task_data_matches_sample=True`. | PASS |

## UAT Items

| Item | Decision | Prompt | Result | Reason If Skipped |
|---|---|---|---|---|
| 1 | D3, D13 | Inspect the generated markdown report for title/date, summary, time blocks, and overflow. | PASS |  |
| 2 | D4, D8, D16 | Start the MCP server and confirm list/add/complete/reset still work over SSE. | PASS |  |
| 3 | D1, D6, D9 | Run the real-key planner CLI and confirm it writes a report. | PASS | Verified in execution log; not rerun during review to avoid an extra LLM call. |
| 4 | D9 | Run the planner CLI with `OPENAI_API_KEY` empty and confirm a clear failure before MCP use. | PASS |  |

## Quality Gates

| Command / Check | Result | Notes |
|---|---|---|
| `uv run pytest` | PASS | 9 tests passed. |
| `$env:OPENAI_API_KEY=''; uv run daily-planner-plan` | PASS | Exited 2 with `OPENAI_API_KEY is required for LLM planning...`. |
| Start `uv run daily-planner-mcp`, then `uv run python -m daily_planner_agent.mcp_client_check` | PASS | Port opened; tools listed; add, complete, and reset succeeded. |
| Compare `data/tasks.sample.json` and `data/tasks.json` after MCP validation | PASS | Printed `task_data_matches_sample=True`. |
| Generated report inspection | PASS | `reports/daily-plan-2026-06-11.md` contains title/date, summary, time-block table, and `Unscheduled overflow`. |
| Git diff review | SKIPPED | Workspace is not a git repository; review used artifact inspection, line-level file reads, and verification commands. |

## Next Route

Ask the user to approve review, then route to the next phase via `$plan-before-code`.
