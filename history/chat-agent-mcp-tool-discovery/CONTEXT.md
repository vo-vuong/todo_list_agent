# Chat Agent MCP Tool Discovery - Context

**Feature slug:** chat-agent-mcp-tool-discovery
**Date:** 2026-06-11
**Clarification status:** complete
**Scope:** Standard
**Domain types:** SEE | CALL | RUN | READ

## Feature Boundary

Extend the Streamlit Chat agent so user chat commands can complete tasks and generate markdown reports by discovering available MCP tools at runtime, choosing the right tool or tools, executing them, and showing the tool-discovery trace in the Chat tab.

## Locked Decisions

These are fixed. Implementation must follow them exactly.

- **D1:** Chat agent must support task completion commands from natural language.
  - Rationale: The current Chat tab only drafts new tasks; this feature adds action execution.
- **D2:** Chat agent must support markdown report generation commands from natural language.
  - Rationale: Report generation must become a chat action, not only a Planner tab or CLI action.
- **D3:** Markdown report generation must be exposed as an MCP tool that the chat agent discovers and selects.
  - Rationale: The app must not bypass the requested tool-discovery behavior by calling the local report writer directly outside the agent action path.
- **D4:** Chat task completion must support both exact `task_id` and task title references. If a title is duplicated or ambiguous, the agent must ask a follow-up question instead of guessing.
- **D5:** The Chat tab must show a short trace for each action turn: MCP tools discovered, selected tool name, arguments passed, and a summary of the result.
- **D6:** Clear side-effect commands execute immediately after the agent understands them; there is no confirmation step for clear complete-task or generate-report commands.
- **D7:** A single chat turn may execute multiple MCP tools in order, such as completing a task and then generating a markdown report in the same user request.
- **D8:** Do not hardcode or pass a specific tool choice to the agent for complete/report commands. The agent must connect to the MCP server, discover available tools, and choose suitable tools from that discovered set.

### Agent's Discretion

Implementation may choose the exact internal structured result shape and trace object names, provided the Chat tab exposes the required trace content and tests can prove MCP discovery happens before tool execution.

## Specific Ideas And References

- User examples include commands like "Xuất file plan markdown" and "hoàn thành task_id và task title sau đó chat agent thực hiện".
- The desired observable behavior is that the user can see which MCP tools were discovered and which tool the agent selected.

## Existing Code Context

From the quick scout. Future agents read these before implementation.

### Reusable Assets

- `src/daily_planner_agent/chat_agent.py` - Current PydanticAI chat task-draft agent and prompt. It only creates task drafts or follow-up questions today.
- `src/daily_planner_agent/streamlit_app.py` - Current Streamlit app with Tasks, Planner, and Chat tabs. Chat state and message rendering already exist here.
- `src/daily_planner_agent/mcp_client.py` - Current SSE MCP client session helper and fixed helper functions for `list_tasks`, `add_task`, `complete_task`, and `reset_tasks`.
- `src/daily_planner_agent/mcp_server.py` - Current FastMCP server exposing task-store tools. It needs a report-generation MCP tool for D3.
- `src/daily_planner_agent/planner.py` - Existing OpenAI/PydanticAI planner used to generate `DailyPlan`.
- `src/daily_planner_agent/reporting.py` - Existing markdown renderer and file writer for `reports/daily-plan-YYYY-MM-DD.md`.
- `tests/test_chat_agent.py` - Existing pure tests around chat prompt/result helpers.
- `tests/test_streamlit_app.py` - Existing tests for Streamlit helper functions.

### Established Patterns

- `streamlit_app.py` wraps async work with `run_async()` and stores UI state in `st.session_state`.
- MCP task mutations should go through MCP, not direct JSON store writes from the UI.
- Missing `OPENAI_API_KEY` should surface as a clear user-facing error before LLM planning/report work.
- Current report files use the existing dated markdown path format `reports/daily-plan-YYYY-MM-DD.md`.

### Integration Points

- `mcp_server.py` needs an MCP tool that generates the markdown report using existing planner and reporting modules.
- `chat_agent.py` or a nearby module needs an agent path that connects to MCP, lists/discovers tools, chooses tools from the discovered set, and executes the selected calls.
- `streamlit_app.py` needs Chat tab rendering for action results and the required tool trace.

## Validation

- Add or update automated tests proving chat action handling records discovered tool names, selected tool name, arguments, and result summary.
- Add or update automated tests proving ambiguous duplicate task titles ask a follow-up question instead of completing a task.
- Add or update automated tests proving a multi-action request can complete a task then generate a report in order.
- Run the existing test suite with `uv run pytest`.
- Manual check with MCP server and Streamlit: in Chat, ask to complete a task by ID, complete a task by title, generate markdown report, and run a combined complete-then-report command; verify the trace is visible for each action turn.

## Open Questions

### Resolve Before Coding

None.

### Deferred To Implementation

- [ ] Exact agent/tool integration API choice within PydanticAI/MCP, as long as D8 is satisfied and tests prove discovery precedes execution.
- [ ] Exact wording and layout of the Chat tab trace, as long as D5 content is visible.

## Deferred Ideas

- Redesigning the report format is out of scope; preserve the existing report renderer unless required for the MCP tool wrapper.
- Changing the Tasks tab or CLI behavior is out of scope except where shared helpers need to support the chat action flow.

## Handoff Note

CONTEXT.md is the source of truth. Decision IDs are stable. Implementation must honor locked decisions, preserve listed patterns, and satisfy validation proof before claiming done.
