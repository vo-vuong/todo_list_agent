# Chat Task Agent - Review

**Feature slug:** chat-task-agent
**Date:** 2026-06-11
**Current work:** Implement a new Streamlit `Chat` tab that drafts tasks from natural language, asks follow-up questions for missing required fields, and saves only confirmed drafts through MCP.
**Execution log:** `history/chat-task-agent/execution-log.md`

## Summary

- P1: 0
- P2: 0
- P3: 1
- Review decision: PASS WITH NON-BLOCKING FINDINGS

## Findings

| Severity | Area | File / Line | Finding | Smallest Fix |
|---|---|---|---|---|
| P3 | test-coverage | `history/chat-task-agent/execution-log.md` | Manual Chat LLM end-to-end UAT was skipped, so the OpenAI-backed draft and follow-up behavior has not been confirmed in the browser with a real API key. Automated tests cover local structured models and helpers, but not live model behavior. | Run the listed manual UAT with a valid `OPENAI_API_KEY` and available browser session. |

## Artifact Verification

| Artifact / Behavior | EXISTS | SUBSTANTIVE | WIRED | Evidence |
|---|---|---|---|---|
| Chat task agent | yes | yes | yes | `src/daily_planner_agent/chat_agent.py:86` exposes `draft_task_from_chat(...)` using PydanticAI/OpenAI structured output. |
| Draft-before-save UI | yes | yes | yes | `src/daily_planner_agent/streamlit_app.py:95` reads draft state; `src/daily_planner_agent/streamlit_app.py:122` saves only through the `Save task` button. |
| MCP persistence path | yes | yes | yes | `src/daily_planner_agent/streamlit_app.py:133` calls existing `add_task(...)` only after confirmation. |
| Missing-field follow-up model | yes | yes | yes | `src/daily_planner_agent/chat_agent.py:44` models either a draft or `follow_up_question`; validator requires `missing_fields` for follow-ups. |
| Tests | yes | yes | yes | `tests/test_chat_agent.py` and `tests/test_streamlit_app.py` added focused non-LLM coverage; `uv run pytest` passed. |
| README update | yes | yes | yes | `README.md` documents Chat tab, task draft behavior, and OpenAI key usage. |

## Decision Coverage

| Decision | Evidence | Result |
|---|---|---|
| D1 | `streamlit_app.py:95-149` keeps a draft in session state and saves only from `_save_chat_draft(...)` after the `Save task` button. | PASS |
| D2 | `chat_agent.py:25-32` makes required draft fields mandatory, and `chat_agent.py:51-60` requires follow-up output when draft is absent. | PASS |

## UAT Items

| Item | Decision | Prompt | Result | Reason If Skipped |
|---|---|---|---|---|
| 1 | D1 | In `Chat`, send a complete task request, confirm a draft appears before save, click `Save task`, and verify it appears in `Tasks`. | SKIPPED | Requires valid OpenAI API key and in-app browser interaction; browser target was unavailable in this session. |
| 2 | D2 | In `Chat`, send an incomplete task request and verify the assistant asks a follow-up question without saving a task. | SKIPPED | Requires valid OpenAI API key and in-app browser interaction; browser target was unavailable in this session. |

## Quality Gates

| Command / Check | Result | Notes |
|---|---|---|
| `uv run pytest` | PASS | 17 tests passed after final cleanup. |
| `uv run python -m compileall src tests` | PASS | Source and tests compiled successfully after final cleanup. |
| Streamlit HTTP probe on `http://localhost:8501` | PASS | Local Streamlit server responded with HTTP 200. |

## Next Route

`$capture-learnings`
