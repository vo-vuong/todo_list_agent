# Chat Agent MCP Tool Discovery - Approach

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Source of truth:** `history/chat-agent-mcp-tool-discovery/CONTEXT.md`

## Repo Reality

- `src/daily_planner_agent/chat_agent.py` - Existing Chat agent is a PydanticAI structured-output flow for task drafts only; it does not execute MCP actions.
- `src/daily_planner_agent/streamlit_app.py` - Existing Chat tab persists messages and drafts in `st.session_state`, while Planner and Tasks tabs already perform report generation and task completion outside chat.
- `src/daily_planner_agent/mcp_client.py` - Existing MCP client can open an SSE `ClientSession`, call fixed tools, and parse structured MCP results, but it has no generic tool discovery/execution trace.
- `src/daily_planner_agent/mcp_server.py` - Existing FastMCP server exposes `list_tasks`, `add_task`, `complete_task`, and `reset_tasks`; it does not expose report generation as a tool.
- `src/daily_planner_agent/planner.py` and `src/daily_planner_agent/reporting.py` - Existing daily plan generation and markdown writing can be reused inside a new MCP report tool.
- `tests/test_chat_agent.py`, `tests/test_streamlit_app.py`, and `tests/test_mcp_client.py` - Existing tests are focused and helper-level; new behavior should keep live OpenAI/MCP work out of unit tests where possible.
- Installed `pydantic-ai` is `1.107.0`; `Agent.__init__` supports `toolsets`, and `pydantic_ai.mcp.MCPServerSSE` supports `process_tool_call`, which can support real MCP tool discovery plus trace capture.

## Chosen Mode And Shape

**Mode:** `small_change`
**Shape:** `work-plan`

Why this is the least workflow that protects the work:

The work touches a few related modules and has clear validation surfaces, but it can ship as one coherent change without user-visible phases.

Why smaller shapes are insufficient, if above `small_change`:

Not applicable.

## Decision Coverage

| Decision | Planning Impact | Covered By |
|---|---|---|
| D1 | Chat must execute task completion commands. | Work-plan steps 2, 4, and validation. |
| D2 | Chat must execute markdown report generation commands. | Work-plan steps 1, 2, 4, and validation. |
| D3 | Report generation must be an MCP-discovered tool. | Work-plan step 1 and MCP discovery validation. |
| D4 | Completion must support task ID and title, with ambiguity follow-up. | Work-plan steps 1-2 and ambiguity tests. |
| D5 | Chat tab must show discovered tools, selected tool, args, and summary. | Work-plan steps 3-4 and UI/helper tests. |
| D6 | Clear side-effect commands execute immediately. | Work-plan steps 2 and 4. |
| D7 | One chat turn can execute multiple tools in order. | Work-plan step 2 and multi-action tests. |
| D8 | Agent must discover MCP tools and choose from the discovered set. | Work-plan steps 2 and validation using MCP toolset/listing trace. |

## Approach

Add the smallest action layer alongside the existing task-draft chat flow. First expand the MCP surface so the server offers the actions the agent is allowed to discover, including a report-generation tool and task-title-friendly completion behavior that can report ambiguity. Then add a chat action agent path that connects to the configured MCP SSE server through PydanticAI MCP tooling, lets the model choose tools from the discovered MCP toolset, and records a trace of discovered tool names and actual calls. Finally wire Streamlit Chat to route ordinary create-task drafting to the existing draft path while action-like requests use the new MCP-discovery action path and render the trace.

## Likely Files

- `src/daily_planner_agent/mcp_server.py` - Add report generation MCP tool and any task-title completion helper exposed through MCP.
- `src/daily_planner_agent/mcp_client.py` - Add generic discovery/execution support or trace-friendly session helpers if needed by tests/UI.
- `src/daily_planner_agent/chat_agent.py` - Add action intent/result models and the MCP-discovery chat action agent path while preserving the existing task-draft flow.
- `src/daily_planner_agent/streamlit_app.py` - Route Chat tab action commands, persist/render trace data, and preserve draft-review behavior for create-task prompts.
- `tests/test_chat_agent.py` - Cover prompt/result helpers, ambiguity behavior, trace model shape, and multi-tool sequencing with fakes.
- `tests/test_streamlit_app.py` - Cover trace formatting helpers and chat state rendering support.
- `tests/test_mcp_client.py` or a new MCP/action test file - Cover structured extraction and generic trace helper behavior without live services.
- `README.md` - Update Chat documentation if implementation changes user-visible commands or requirements.

## Risks

- Live agent validation depends on `OPENAI_API_KEY`; automated tests should use fakes for selection/order and reserve real-key checks for manual validation.
- D8 forbids hardcoded tool choice for execution, so implementation must avoid shortcutting clear commands directly to `complete_task` or report writer outside the MCP-discovered tool path.
- Title matching can be ambiguous; completion by title must be resolved through a deterministic tool result or follow-up, not silent first-match behavior.
- Report generation inside the MCP server may call the planner and therefore needs the same missing-key behavior as current Planner/CLI flows.

## Validation Needs

- Unit tests proving discovered MCP tool names and selected calls are captured in the chat action trace.
- Unit tests proving duplicate task titles produce a follow-up and no completion.
- Unit tests proving a combined complete-then-report command records the selected tools in order.
- Existing suite: `uv run pytest`.
- Manual check with MCP server and Streamlit Chat for complete by ID, complete by title, generate report, and combined complete-then-report commands.

## Handoff

Use this approach plus the selected shape artifact before editing code. Do not expand scope beyond `CONTEXT.md` without returning to clarification.
