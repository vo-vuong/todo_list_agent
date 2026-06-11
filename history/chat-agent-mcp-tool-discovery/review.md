# Chat Agent MCP Tool Discovery - Review

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Current work:** Implement chat-driven MCP action execution for completing tasks and generating markdown reports, with visible per-turn discovery/selection trace in the Streamlit Chat tab.
**Execution log:** `history/chat-agent-mcp-tool-discovery/execution-log.md`

## Summary

- P1: 0
- P2: 0
- P3: 1
- Review decision: PASS WITH NON-BLOCKING FINDINGS

## Findings

| Severity | Area | File / Line | Finding | Smallest Fix |
|---|---|---|---|---|
| P3 | test-coverage | `tests/test_chat_agent.py:116` | The current automated coverage proves discovery-before-agent-run and tool-call trace order using fakes, while `tests/test_mcp_server.py:34` proves duplicate-title handling at the MCP helper level. It does not exercise a real LLM/MCPToolset completion-by-title turn end to end. This leaves a small residual risk that prompt/tool-selection behavior for title completion could drift even though the core helper and trace behavior are covered. | Add a manual UAT record or a controlled integration test that runs the chat action path against a temporary MCP server/task store for a unique title and an ambiguous title. |

## Artifact Verification

| Artifact / Behavior | EXISTS | SUBSTANTIVE | WIRED | Evidence |
|---|---|---|---|---|
| MCP report generation tool | yes | yes | yes | `src/daily_planner_agent/mcp_server.py:141` exposes `generate_daily_report`; `generate_daily_report_result()` calls planner/report writer; real smoke selected `generate_daily_report`. |
| MCP completion by ID/title | yes | yes | yes | `src/daily_planner_agent/mcp_server.py:113` exposes `complete_task_by_reference`; helper handles exact ID, unique title, ambiguous title, and not found at `mcp_server.py:186`; tests cover exact ID and ambiguity. |
| MCP tool descriptions for agent choice | yes | yes | yes | Detailed descriptions are present in `mcp_server.py:31`, `mcp_server.py:56`, `mcp_server.py:93`, `mcp_server.py:113`, `mcp_server.py:141`, and `mcp_server.py:164`; `tests/test_mcp_server.py:66` asserts key guidance appears through FastMCP metadata. |
| Chat action agent path | yes | yes | yes | `src/daily_planner_agent/chat_agent.py:175` discovers tools, creates `MCPToolset`, and runs the PydanticAI agent; `tests/test_chat_agent.py:116` verifies discovery precedes agent execution. |
| Visible Chat trace | yes | yes | yes | `src/daily_planner_agent/streamlit_app.py:212` formats discovered tools, selected tool, args, and result summary; `_render_chat_action_traces()` renders the trace at `streamlit_app.py:271`; `tests/test_streamlit_app.py:75` covers the row shape. |
| Dependency support for MCPToolset | yes | yes | yes | `pyproject.toml:10` uses `pydantic-ai-slim[mcp,openai]`; `uv.lock` includes the MCP extra and `fastmcp-slim`; real smoke passed after `uv sync`. |
| README user guidance | yes | yes | yes | `README.md` documents Chat action commands and trace behavior in the Streamlit section. |

## Decision Coverage

| Decision | Evidence | Result |
|---|---|---|
| D1 | `complete_task_by_reference` MCP tool and Chat action routing in `streamlit_app.py:111`; tests cover completion helper and trace callback. | PASS |
| D2 | `generate_daily_report` MCP tool at `mcp_server.py:141`; real smoke selected it and wrote `reports/daily-plan-2026-06-11.md`. | PASS |
| D3 | Report generation is only added as an MCP tool for Chat action path; real smoke trace selected `generate_daily_report`. | PASS |
| D4 | `complete_task_by_reference_result()` resolves exact ID/unique title and returns `needs_clarification` on duplicate title; `tests/test_mcp_server.py:34` verifies no completion on ambiguity. | PASS |
| D5 | `ChatActionTrace`, `ChatToolCallTrace`, and `action_trace_rows()` expose discovered tools, selected tool, arguments, and result summary; tests verify row content. | PASS |
| D6 | `_handle_chat_action()` executes immediately after `looks_like_action_request()` at `streamlit_app.py:111` without a confirm step. | PASS |
| D7 | `_build_process_tool_call()` appends calls in order; `tests/test_chat_agent.py:100` verifies complete-then-report ordering. | PASS |
| D8 | `run_chat_action_from_chat()` calls `discover_tools()` before constructing/running the agent, then uses `MCPToolset`; `tests/test_chat_agent.py:167` asserts ordering. | PASS |

## UAT Items

| Item | Decision | Prompt | Result | Reason If Skipped |
|---|---|---|---|---|
| 1 | D2, D3, D5, D8 | `Xuất file plan markdown cho hôm nay.` | PASS | Real smoke in execution log discovered 6 tools and selected `generate_daily_report`. |
| 2 | D1, D4, D5, D8 | Complete a task by exact ID in Chat. | SKIPPED | Not rerun during review; covered by helper/fake tests and should be confirmed in Streamlit UAT. |
| 3 | D1, D4, D5, D8 | Complete a task by unique title in Chat. | SKIPPED | Not rerun during review; residual P3 coverage gap records this. |
| 4 | D4 | Complete an ambiguous duplicate title in Chat and confirm follow-up. | SKIPPED | Not rerun during review; MCP helper test covers no-mutation ambiguity behavior. |
| 5 | D5 | Visually inspect Chat trace rows in Streamlit. | SKIPPED | In-app Browser was unavailable; HTTP smoke only confirmed Streamlit served. |

## Quality Gates

| Command / Check | Result | Notes |
|---|---|---|
| `uv run pytest` | PASS | 26 tests passed during review. |
| Diff inspection | PASS | Source, dependency, README, and tests inspected against `CONTEXT.md`, `work-plan.md`, `validation.md`, and `execution-log.md`. |
| Live MCP description probe | PASS | Execution log records `complete_task_by_reference` and `generate_daily_report` descriptions exposed through MCP `list_tools()`. |
| Real report action smoke | PASS | Execution log records report action trace selecting `generate_daily_report`. |
| Streamlit browser UAT | SKIPPED | Browser `iab` unavailable in this session; Streamlit HTTP smoke passed in execution log. |

## Next Route

`$capture-learnings`
