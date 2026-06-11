# Chat Agent MCP Tool Discovery - Execution Log

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Current work:** Implement chat-driven MCP action execution for completing tasks and generating markdown reports, with visible per-turn discovery/selection trace in the Streamlit Chat tab.
**Plan:** `history/chat-agent-mcp-tool-discovery/work-plan.md`
**Validation:** `history/chat-agent-mcp-tool-discovery/validation.md`

## Files Changed

- `src/daily_planner_agent/mcp_server.py` - Added `complete_task_by_reference` and `generate_daily_report` MCP tools, plus testable helper functions for title ambiguity and report generation.
- `src/daily_planner_agent/mcp_server.py` - Expanded MCP tool docstrings with selection guidance, arguments, return shapes, and side effects so the agent can choose tools more reliably from discovery metadata.
- `src/daily_planner_agent/mcp_client.py` - Added `discover_tools()` and `McpToolInfo` for trace-friendly MCP discovery.
- `src/daily_planner_agent/chat_agent.py` - Added chat action models, action prompt, MCP toolset execution path, action request detection, and tool-call trace capture.
- `src/daily_planner_agent/streamlit_app.py` - Routed action-like Chat prompts to the new action path and rendered per-turn MCP trace rows in the Chat tab.
- `pyproject.toml` - Changed PydanticAI dependency to `pydantic-ai-slim[mcp,openai]` because `MCPToolset` requires the MCP extra.
- `uv.lock` - Updated dependency lock to include the MCP client extra and `fastmcp-slim`.
- `tests/test_chat_agent.py` - Added tests for action prompt discovery, action routing, trace capture, multi-tool order, and discovery-before-agent-run behavior.
- `tests/test_streamlit_app.py` - Added trace row formatting coverage.
- `tests/test_mcp_server.py` - Added completion-by-reference tests for exact ID success and ambiguous title follow-up.
- `tests/test_mcp_server.py` - Added coverage that MCP tool descriptions include selection guidance for completion, report generation, and read-only task listing.
- `README.md` - Documented Chat action commands and the visible MCP trace.

## Decisions Honored

| Decision | How implementation honored it |
|---|---|
| D1 | Chat action path can execute completion through MCP-discovered tools; MCP server exposes `complete_task_by_reference`. |
| D2 | Chat action path can execute report generation through MCP; MCP server exposes `generate_daily_report`. |
| D3 | Report generation is an MCP tool and the real smoke selected `generate_daily_report` through the agent action path. |
| D4 | `complete_task_by_reference_result()` handles exact task ID, unique title, ambiguous title, and not-found cases without guessing. |
| D5 | `ChatActionTrace` and Streamlit `action_trace_rows()` expose discovered tools, selected tool, arguments, and result summary. |
| D6 | Streamlit action prompts execute immediately via `_handle_chat_action()` without a confirmation step. |
| D7 | Tool-call trace preserves call order; tests cover complete-then-report order through the callback. |
| D8 | `run_chat_action_from_chat()` discovers MCP tools first, then creates a PydanticAI agent with `MCPToolset`; tests assert discovery happens before agent run. |

## Implementation Notes

- The existing create-task draft flow is preserved for prompts that do not look action-like.
- `complete_task(task_id)` is preserved for the existing CLI and Tasks tab.
- MCP tool docstrings now intentionally describe when to use each tool, what arguments to pass, return status values, and whether the tool has side effects because these descriptions are visible during tool discovery.
- Real smoke testing exposed a missing runtime dependency for `MCPToolset`; adding the `mcp` extra fixed it.
- In-app Browser was unavailable for this session (`iab` not available), so UI verification used an HTTP Streamlit smoke check instead of browser DOM inspection.

## Deviations From Plan

- Added `pyproject.toml` and `uv.lock` changes, which were not listed as likely files, because real runtime validation proved `pydantic-ai-slim[openai]` was insufficient for MCP toolsets.

## Verification

| Command / Check | Result | Notes |
|---|---|---|
| `uv run pytest` | PASS | 26 tests passed after adding MCP docstring guidance coverage. |
| Live MCP discovery on `MCP_SERVER_URL=http://localhost:8765/sse` | PASS | `list_tools()` returned `list_tasks`, `add_task`, `complete_task`, `complete_task_by_reference`, `generate_daily_report`, `reset_tasks`. |
| Live MCP description probe on `MCP_SERVER_URL=http://localhost:8765/sse` | PASS | `complete_task_by_reference` and `generate_daily_report` descriptions include tool selection guidance through MCP `list_tools()`. |
| Real chat-action smoke: `Xuất file plan markdown cho hôm nay.` | PASS | Agent discovered 6 MCP tools and selected `generate_daily_report` with `{}` args; report written to `reports/daily-plan-2026-06-11.md`. |
| Streamlit HTTP smoke on `http://localhost:8502` | PASS | Returned `status=200` and contained Streamlit content. |
| In-app Browser verification | SKIPPED | Browser plugin was present but `iab` browser was unavailable in this session. |
| First real chat-action smoke before dependency fix | FAIL then fixed | Failed with missing `fastmcp`; fixed by adding `pydantic-ai-slim[mcp,openai]` and running `uv sync`. |

## Remaining Work

- Run `$review-after-code` before considering the work complete.

## Handoff

Ready for `$review-after-code`: yes
