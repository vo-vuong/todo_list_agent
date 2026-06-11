# Chat Agent MCP Tool Discovery - Validation

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Mode:** small_change
**Current work:** Implement chat-driven MCP action execution for completing tasks and generating markdown reports, with visible per-turn discovery/selection trace in the Streamlit Chat tab.
**Source of truth:** `history/chat-agent-mcp-tool-discovery/CONTEXT.md`
**Plan:** `history/chat-agent-mcp-tool-discovery/work-plan.md`

## Reality Gate

| Check | Result | Evidence |
|---|---|---|
| Mode fit | PASS | `work-plan.md` scopes one coherent change across MCP server, chat agent, Streamlit Chat, and tests; no phase-shaped dependency is required. |
| Repo fit | PASS | `src/daily_planner_agent/chat_agent.py` has the existing chat draft path, `streamlit_app.py` has Chat rendering/state, `mcp_server.py` exposes FastMCP tools, and `planner.py`/`reporting.py` already generate markdown reports. |
| Assumptions | PASS | Runtime probes confirmed PydanticAI has `Agent(..., toolsets=...)`, `pydantic_ai.mcp.MCPServerSSE` has `process_tool_call`, and MCP `ClientSession` has `list_tools` and `call_tool`. |
| Smaller path | PASS | Direct task is too small because D3/D5/D8 require MCP server expansion, action agent integration, trace capture, and UI rendering; `small_change` is the smallest honest shape. |
| Proof surface | PASS | `uv run pytest` passes; live MCP server probe listed current tools over SSE; work plan has specific tests and manual checks for complete-by-ID, complete-by-title, report, ambiguity, and multi-tool order. |

## Feasibility Matrix

| Part / Assumption | Risk | Proof Required | Evidence | Result |
|---|---|---|---|---|
| Existing tests are healthy before implementation. | LOW | Run baseline suite. | `uv run pytest` collected 17 tests and all 17 passed in 2.38s. | PASS |
| MCP server can be started and discovered over SSE. | LOW | Start `uv run daily-planner-mcp` and call `ClientSession.list_tools()`. | Live probe returned `['list_tasks', 'add_task', 'complete_task', 'reset_tasks']` without mutating task data. | PASS |
| Current MCP surface lacks report generation, so D3 requires a new MCP tool. | LOW | Inspect current server tools and live list output. | `src/daily_planner_agent/mcp_server.py` defines `list_tasks`, `add_task`, `complete_task`, and `reset_tasks`; live probe returned the same 4 tools. | PASS |
| PydanticAI can connect to MCP tools rather than hardcoded local helpers. | MEDIUM | Verify installed API supports MCP toolsets. | Probe showed `Agent.__init__` contains `toolsets` and `MCPServerSSE.__init__` supports `process_tool_call`. | PASS |
| Tool discovery and execution can be traced. | MEDIUM | Verify MCP and PydanticAI hooks expose list/call points. | Probe showed `ClientSession.list_tools`, `ClientSession.call_tool`, and `MCPServerSSE(process_tool_call=...)` are available. | PASS |
| Markdown report generation can reuse existing planner/report code. | LOW | Inspect importable modules. | `planner.py` exposes `generate_daily_plan`; `reporting.py` exposes `write_markdown_report` and `render_markdown_report`; Planner tab already uses these in `_generate_report()`. | PASS |
| Report generation full flow can run in the local environment. | MEDIUM | Confirm OpenAI settings without printing secrets. | Probe showed `OPENAI_API_KEY_present=True` and `OPENAI_MODEL=gpt-5-nano`. | PASS WITH CONSTRAINT |
| Completion by title can be implemented without hidden architecture. | MEDIUM | Confirm tasks have title/id fields and store can list tasks. | `models.py` task schema has `id`, `title`, and `completed`; `store.py`/MCP server already list and complete tasks by ID. | PASS |
| Streamlit Chat can render trace state without UI rewrite. | LOW | Inspect current Chat state functions. | `streamlit_app.py` already renders chat messages from `st.session_state` and can add helper rendering for trace objects. | PASS |

## Probes

- Baseline tests: `uv run pytest` -> PASS, 17 passed.
- PydanticAI/MCP API probe:
  - `Agent.toolsets_supported=True`
  - `MCPServerSSE.process_tool_call_supported=True`
  - `ClientSession.list_tools=True`
  - `ClientSession.call_tool=True`
- Live MCP discovery probe:
  - Started `uv run daily-planner-mcp`.
  - Called `ClientSession.list_tools()` against configured SSE URL.
  - Result: `['list_tasks', 'add_task', 'complete_task', 'reset_tasks']`.
  - Stopped the server process after probe.
- Credential probe:
  - `OPENAI_API_KEY_present=True`
  - `OPENAI_MODEL=gpt-5-nano`

## Integration Readiness

- MCP server can add report generation without changing task JSON storage shape because planner/report modules already consume `Task` objects and write dated markdown files.
- Chat action execution can use PydanticAI MCP toolsets for the agent-visible tool surface, while trace capture can use MCP discovery and `process_tool_call`/session call data.
- Streamlit Chat already has a stateful rendering loop and async wrapper, so action results and trace rows can be added without restructuring the app.
- Existing CLI and Tasks tab can remain compatible if the current `complete_task(task_id)` MCP tool is preserved.

## Verification Readiness

- Automated: `uv run pytest`.
- Automated additions during implementation:
  - Trace records discovered tool names, selected tool name, arguments, result summary, and call order.
  - Duplicate task title completion asks a follow-up and does not complete a task.
  - Combined complete-then-report request records tool calls in order.
  - Streamlit trace formatting helper exposes all required D5 fields.
- Manual:
  - Start MCP server with `uv run daily-planner-mcp`.
  - Run Streamlit with `uv run streamlit run src/daily_planner_agent/streamlit_app.py`.
  - In Chat, verify complete by ID, complete by title, ambiguous title follow-up, report markdown generation, and combined complete-then-report, with visible discovery trace.

## Decision

READY WITH CONSTRAINTS

## Constraints For Implementation

- Do not execute chat complete/report actions by directly calling fixed Streamlit helpers such as `complete_task` or `write_markdown_report`; action execution must go through MCP-discovered tools.
- Preserve the existing task-draft flow for create-task chat prompts unless the prompt is routed as an action command.
- Preserve existing CLI and Tasks tab compatibility by keeping `complete_task(task_id)` behavior.
- Keep unit tests free of real OpenAI calls; use fakes for tool-choice and trace assertions.
- Manual report validation requires running the MCP server and using the configured OpenAI key.

## Approval

Execution approved: no
Implementation may start only after this changes to yes in conversation and
`.khuym/state.json` has `approved_gates.execution = true`.
