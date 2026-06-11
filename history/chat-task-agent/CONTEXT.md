# Chat Task Agent - Context

**Feature slug:** chat-task-agent
**Date:** 2026-06-11
**Clarification status:** complete
**Scope:** Standard
**Domain types:** SEE | CALL | ORGANIZE

## Feature Boundary

Add a new Streamlit `Chat` tab that lets users talk to an agent to draft a task from natural language, ask follow-up questions for missing required task fields, and save the confirmed draft through the existing MCP `add_task` flow.

## Locked Decisions

These are fixed. Implementation must follow them exactly.

- **D1:** The Chat agent must create a task draft first and must not write directly to `data/tasks.json`.
  - Rationale: Users need to review the parsed task before any MCP write happens.
- **D2:** If the user's text is missing required task creation details, the Chat agent must ask follow-up questions in the chat instead of filling defaults.
  - Rationale: Task creation currently requires title, due date, estimated minutes, and priority; silently choosing defaults would create inaccurate work items.

### Agent's Discretion

The implementation may choose the exact chat copy, session state keys, parsing prompt shape, and UI controls, as long as the new flow preserves the existing Streamlit style and uses the existing MCP client for persistence.

## Specific Ideas And References

- User requested a new Streamlit tab named `Chat`.
- User wants the chat to interact with the agent and create tasks from text.
- User explicitly prefers draft-before-save and follow-up questions for missing fields.

## Existing Code Context

From the quick scout. Future agents read these before implementation.

### Reusable Assets

- `src/daily_planner_agent/streamlit_app.py` - Existing Streamlit app with `Tasks` and `Planner` tabs, session state report handling, and MCP client calls.
- `src/daily_planner_agent/mcp_client.py` - Existing async MCP client functions, including `add_task`.
- `src/daily_planner_agent/planner.py` - Existing PydanticAI/OpenAI setup pattern and missing-key behavior.
- `src/daily_planner_agent/models.py` - Existing `TaskCreate`, `Task`, and `Priority` schemas to reuse for draft validation.
- `src/daily_planner_agent/store.py` - Existing task validation and persistence behavior behind MCP.

### Established Patterns

- `src/daily_planner_agent/streamlit_app.py` - UI operations call MCP client functions via `run_async`; errors are displayed with `st.error`; successful writes call `st.rerun()`.
- `src/daily_planner_agent/planner.py` - LLM functionality checks `OPENAI_API_KEY` before use and raises `MissingOpenAIKeyError` with a clear message.
- `tests/test_streamlit_app.py` - Streamlit helper functions are tested as pure functions when possible.

### Integration Points

- `src/daily_planner_agent/streamlit_app.py` - Add the third tab and render chat workflow.
- `src/daily_planner_agent/mcp_client.py` - Use existing `add_task` to persist confirmed drafts.
- `src/daily_planner_agent/models.py` - Validate draft output against existing task creation constraints.
- `pyproject.toml` - Existing dependencies include PydanticAI/OpenAI and Streamlit; no new dependency should be needed unless implementation evidence proves otherwise.

## Validation

- `uv run pytest`
- Manual Streamlit check: start `uv run daily-planner-mcp`, then `uv run streamlit run src/daily_planner_agent/streamlit_app.py`, open `Chat`, send a complete task request, verify a draft is shown, confirm it, and verify the task appears in `Tasks`.
- Manual Streamlit check: send an incomplete task request and verify the chat asks a follow-up question instead of saving or showing a complete draft.

## Open Questions

### Resolve Before Coding

- None.

### Deferred To Implementation

- Choose the exact structured output model for the chat agent.
- Choose how to represent partial draft state in `st.session_state`.
- Choose the minimal tests for parsing result handling and Streamlit helper behavior.

## Deferred Ideas

- Editing existing tasks through chat - out of scope for this feature.
- Completing tasks through chat - out of scope because the request is specifically task creation from text.
- Multi-turn planning conversations beyond collecting missing task fields - out of scope for this feature.

## Handoff Note

CONTEXT.md is the source of truth. Decision IDs are stable. Implementation must
honor locked decisions, preserve listed patterns, and satisfy validation proof
before claiming done.
