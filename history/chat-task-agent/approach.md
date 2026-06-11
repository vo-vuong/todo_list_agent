# Chat Task Agent - Approach

**Feature slug:** chat-task-agent
**Date:** 2026-06-11
**Source of truth:** `history/chat-task-agent/CONTEXT.md`

## Repo Reality

- `src/daily_planner_agent/streamlit_app.py` - Existing Streamlit app has two tabs, wraps async MCP calls with `run_async`, stores UI state in `st.session_state`, and shows errors inline.
- `src/daily_planner_agent/planner.py` - Existing OpenAI/PydanticAI code builds an `OpenAIResponsesModel`, validates structured output, and raises `MissingOpenAIKeyError` before LLM work.
- `src/daily_planner_agent/models.py` - Existing `TaskCreate` model already represents the required create-task fields and should be reused for draft validation.
- `src/daily_planner_agent/mcp_client.py` - Existing `add_task` function persists tasks through MCP and should remain the only save path from the chat flow.
- `tests/test_streamlit_app.py` and `tests/test_planner.py` - Existing tests prefer pure helper assertions and monkeypatching over full UI automation.

## Chosen Mode And Shape

**Mode:** `small_change`
**Shape:** `work-plan`

Why this is the least workflow that protects the work:

The feature needs a few coordinated edits across UI, agent parsing, and tests, but the behavior is bounded and can be validated with focused unit tests plus one manual Streamlit check.

Why smaller shapes are insufficient, if above `small_change`:

This is more than a direct task because it adds a new user-facing tab, LLM structured output behavior, draft state, follow-up behavior, and MCP persistence wiring.

## Decision Coverage

| Decision | Planning Impact | Covered By |
|---|---|---|
| D1 | Chat must show a draft and wait for explicit confirmation before calling MCP `add_task`. | Work plan steps 2, 3, and validation. |
| D2 | Missing required task fields must produce a chat follow-up question instead of defaults or persistence. | Work plan steps 1, 2, and validation. |

## Approach

Add a focused chat task agent path that returns structured output describing either a complete `TaskCreate` draft or a follow-up question with missing fields. Streamlit will render a third `Chat` tab, preserve conversation/draft state in `st.session_state`, display the draft for review, and only call existing MCP `add_task` when the user confirms. The implementation should reuse the existing OpenAI setup and missing-key behavior instead of introducing new dependencies.

## Likely Files

- `src/daily_planner_agent/models.py` - Add structured models for chat task draft results if they are shared beyond one module.
- `src/daily_planner_agent/chat_agent.py` - Add the natural-language-to-task-draft agent and prompt.
- `src/daily_planner_agent/streamlit_app.py` - Add `Chat` tab, render chat messages, show draft review UI, and save confirmed drafts through `add_task`.
- `tests/test_streamlit_app.py` - Add pure helper coverage for draft display/session behavior if useful.
- `tests/test_chat_agent.py` - Add coverage for prompt/result helper behavior without calling OpenAI.

## Risks

- PydanticAI structured output needs to distinguish follow-up questions from complete drafts clearly enough to avoid invalid partial `TaskCreate` objects.
- Streamlit reruns can duplicate chat messages or lose draft state if session keys are not kept simple and stable.
- The flow needs a clear missing-key error in Chat, matching the existing Planner behavior.

## Validation Needs

- `uv run pytest`
- Manual check with MCP server and Streamlit: complete natural-language task request shows a draft and saves only after confirmation.
- Manual check with MCP server and Streamlit: incomplete request asks a follow-up question and does not save a task.

## Handoff

Use this approach plus the selected shape artifact before editing code. Do not
expand scope beyond `CONTEXT.md` without returning to clarification.
