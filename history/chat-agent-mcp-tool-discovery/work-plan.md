# Chat Agent MCP Tool Discovery - Work Plan

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Mode:** small_change
**Shape:** work-plan
**Phase:** none
**Source of truth:** `history/chat-agent-mcp-tool-discovery/CONTEXT.md`

## Approved Context

- CONTEXT.md approved: yes
- Phase plan approved: not required
- Current work approved: no

## Decision Coverage

| Decision | Required Behavior | Covered By |
|---|---|---|
| D1 | Chat can complete tasks from natural language. | Steps 1, 2, 4, and validation. |
| D2 | Chat can generate markdown reports from natural language. | Steps 1, 2, 4, and validation. |
| D3 | Report generation is exposed and executed as an MCP tool. | Step 1 and report command validation. |
| D4 | Completion supports task ID and task title, with ambiguity follow-up. | Steps 1-2 and ambiguity tests. |
| D5 | Chat shows discovered tools, selected tool, arguments, and result summary. | Steps 2-4 and trace UI tests. |
| D6 | Clear side-effect commands execute immediately. | Steps 2 and 4. |
| D7 | One turn can execute multiple MCP tools in order. | Step 2 and multi-action tests. |
| D8 | Agent discovers MCP tools and chooses from that discovered set. | Step 2 and trace/discovery validation. |

## Current Work

Implement chat-driven MCP action execution for completing tasks and generating markdown reports, with visible per-turn discovery/selection trace in the Streamlit Chat tab.

## Files Likely To Change

- `src/daily_planner_agent/mcp_server.py` - Add MCP report-generation tool and task-title-aware completion support.
- `src/daily_planner_agent/mcp_client.py` - Add generic MCP discovery/trace support if needed for the chat action path.
- `src/daily_planner_agent/chat_agent.py` - Add MCP action agent/result models and execution path while preserving task drafting.
- `src/daily_planner_agent/streamlit_app.py` - Integrate action results into Chat tab and render trace.
- `tests/test_chat_agent.py` - Add focused action behavior tests.
- `tests/test_streamlit_app.py` - Add trace formatting/render helper tests.
- `tests/test_mcp_client.py` or `tests/test_chat_actions.py` - Add MCP discovery/execution helper tests.
- `README.md` - Document the new Chat action commands and visible MCP trace if needed.

## Implementation Steps

1. Extend MCP server capabilities:
   - Add an MCP tool that generates the daily markdown report using existing `list_todays_tasks`, `generate_daily_plan`, and `write_markdown_report` behavior.
   - Add or adapt MCP completion support so task completion by exact ID and by title can be invoked through discovered MCP tools, returning an explicit ambiguity/follow-up result when multiple titles match.
   - Preserve existing `complete_task(task_id)` behavior for current Tasks tab and CLI callers.

2. Add chat action agent path with MCP discovery:
   - Use the configured MCP SSE server and PydanticAI MCP integration or equivalent MCP session discovery so available MCP tools are listed before execution.
   - Let the agent choose tools from the discovered MCP toolset for complete/report commands; do not route action commands directly to fixed local helpers.
   - Capture a per-turn trace containing discovered tool names, selected tool name, arguments, result summary, and call order.
   - Support multi-tool turns where the model completes a task and then generates a report.

3. Add deterministic helpers around ambiguity and trace formatting:
   - Keep title ambiguity handling testable without live OpenAI.
   - Format trace data for Streamlit without hiding discovered tools or tool arguments.

4. Wire Streamlit Chat:
   - Detect or route action-like chat prompts to the new MCP action path while preserving the existing draft-task flow for task creation.
   - Append assistant messages that summarize completed task/report outcomes.
   - Render the trace for each action turn in Chat.
   - Surface missing `OPENAI_API_KEY` and MCP connection errors clearly.

5. Add tests and docs:
   - Cover trace capture, duplicate-title follow-up, and combined complete-then-report order with fakes.
   - Cover Streamlit trace formatting helpers.
   - Update README Chat section if user-facing commands or setup steps change.

## Validation

- `uv run pytest`
- Manual: start MCP server with `uv run daily-planner-mcp`.
- Manual: run Streamlit with `uv run streamlit run src/daily_planner_agent/streamlit_app.py`.
- Manual in Chat: ask to complete a task by ID and verify the trace shows discovered tools, selected completion tool, args, and result summary.
- Manual in Chat: ask to complete a task by title and verify success when unique.
- Manual in Chat: create duplicate task titles or use existing ambiguous titles and verify the assistant asks a follow-up instead of completing.
- Manual in Chat: ask to generate/export the markdown report and verify the trace shows the report MCP tool selected and `reports/daily-plan-YYYY-MM-DD.md` exists.
- Manual in Chat: ask a combined complete-then-report command and verify selected tool calls appear in order.

## Risks And Constraints

- Do not satisfy report generation by calling `write_markdown_report` directly from Streamlit Chat outside the MCP-discovered tool path.
- Do not satisfy task completion by directly calling `complete_task` from Streamlit Chat outside the MCP-discovered tool path.
- Keep the existing task draft review/save behavior intact for create-task prompts unless an action command is clearly being handled.
- Automated tests should avoid real OpenAI calls; use fakes for action selection and trace assertions.
- Manual full-flow validation requires the MCP server and `OPENAI_API_KEY` for report generation.

## Out Of Scope

- Redesigning the markdown report content or file naming.
- Changing CLI behavior except where shared MCP server behavior remains compatible.
- Reworking the Tasks or Planner tab UI beyond shared helper compatibility.
- Adding unrelated chat actions such as delete, reset, or edit task.

## Approval

Work plan approved: no
Implementation may start only after this changes to yes in the conversation
and `.khuym/state.json` has `approved_gates.work_shape = true`.
