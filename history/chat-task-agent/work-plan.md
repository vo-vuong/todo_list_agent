# Chat Task Agent - Work Plan

**Feature slug:** chat-task-agent
**Date:** 2026-06-11
**Mode:** small_change
**Shape:** work-plan
**Phase:** none
**Source of truth:** `history/chat-task-agent/CONTEXT.md`

## Approved Context

- CONTEXT.md approved: yes
- Phase plan approved: not required
- Current work approved: no

## Decision Coverage

| Decision | Required Behavior | Covered By |
|---|---|---|
| D1 | A parsed task is shown as a draft and is saved only after user confirmation. | Steps 2-4 and manual validation. |
| D2 | Missing title, due date, estimated minutes, or priority causes a follow-up chat question instead of a saved or complete draft. | Steps 1-3 and tests. |

## Current Work

Implement a new Streamlit `Chat` tab that lets the user ask an LLM-backed task agent to draft a task from natural language, asks follow-up questions for missing required fields, and persists only confirmed drafts through the existing MCP `add_task` client.

## Files Likely To Change

- `src/daily_planner_agent/models.py` - Add chat task draft/result models if shared schemas belong with other Pydantic models.
- `src/daily_planner_agent/chat_agent.py` - Add OpenAI/PydanticAI task-draft agent, instructions, and prompt builder.
- `src/daily_planner_agent/streamlit_app.py` - Add `Chat` tab, chat history rendering, draft review, and confirm-save behavior.
- `tests/test_chat_agent.py` - Add pure tests for prompt construction or structured result helpers.
- `tests/test_streamlit_app.py` - Add helper tests for draft formatting/options if implementation introduces pure helpers.
- `README.md` - Update briefly only if commands/features materially change.

## Implementation Steps

1. Add a structured chat task result model and `draft_task_from_chat(...)` function that returns either a complete `TaskCreate` draft or a follow-up question with missing fields; reuse `require_openai_api_key()` behavior.
2. Add Streamlit session state helpers for chat messages and current draft so reruns preserve the conversation without duplicating saves.
3. Add a `Chat` tab to `main()` and render a chat input that calls the task agent, appends assistant responses, and displays a draft review section when a complete draft exists.
4. Wire the draft confirmation button to existing MCP `add_task(...)`, then clear the draft and append a success chat message only after MCP save succeeds.
5. Add focused tests for non-LLM helper behavior and structured prompt/result handling; avoid live OpenAI calls in tests.
6. Update README if needed to mention the new Chat tab and the draft-before-save behavior.

## Validation

- `uv run pytest`
- Manual Streamlit check:
  - Terminal 1: `uv run daily-planner-mcp`
  - Terminal 2: `uv run streamlit run src/daily_planner_agent/streamlit_app.py`
  - In `Chat`, send a complete task request and verify a draft appears without saving immediately.
  - Confirm the draft and verify the task appears in `Tasks`.
  - Send an incomplete task request and verify the assistant asks a follow-up question and no task is saved.

## Risks And Constraints

- Do not bypass MCP persistence; confirmed drafts must use existing `mcp_client.add_task`.
- Do not silently default missing required fields; ask follow-up questions instead.
- Do not introduce live OpenAI calls in automated tests.
- Keep the Chat tab consistent with the existing simple Streamlit UI style.

## Out Of Scope

- Editing existing tasks through chat.
- Completing tasks through chat.
- General planning conversation beyond collecting details for task creation.

## Approval

Work plan approved: no
Implementation may start only after this changes to yes in the conversation
and `.khuym/state.json` has `approved_gates.work_shape = true`.
