# Chat Task Agent - Validation

**Feature slug:** chat-task-agent
**Date:** 2026-06-11
**Mode:** small_change
**Current work:** Implement a new Streamlit `Chat` tab that drafts tasks from natural language, asks follow-up questions for missing required fields, and saves only confirmed drafts through MCP.
**Source of truth:** `history/chat-task-agent/CONTEXT.md`
**Plan:** `history/chat-task-agent/work-plan.md`

## Reality Gate

| Check | Result | Evidence |
|---|---|---|
| Mode fit | PASS | Work spans one Streamlit tab, one focused agent helper, and tests; no phase-shaped milestone is needed. |
| Repo fit | PASS | `src/daily_planner_agent/streamlit_app.py` already uses `st.session_state`, async wrappers, and MCP client calls; `src/daily_planner_agent/planner.py` already shows the OpenAI/PydanticAI setup. |
| Assumptions | PASS | `uv run python -c "import streamlit as st; print(hasattr(st, 'chat_input'), hasattr(st, 'chat_message'))"` returned `True True`. |
| Smaller path | PASS | A direct edit is too small because the work must coordinate LLM structured output, UI draft state, MCP persistence, and tests. |
| Proof surface | PASS | Existing suite runs with `uv run pytest`; manual Streamlit checks are explicit in the work plan. |

## Feasibility Matrix

| Part / Assumption | Risk | Proof Required | Evidence | Result |
|---|---|---|---|---|
| Streamlit Chat UI | LOW | Streamlit supports chat primitives and existing app uses session state. | Probe returned `True True`; `streamlit_app.py` already reads/writes `st.session_state`. | PASS |
| LLM structured task result | MEDIUM | Existing PydanticAI dependency and pattern can create structured outputs. | `planner.py` imports `Agent`, `OpenAIResponsesModel`, and uses `output_type=DailyPlan`. | PASS |
| Confirm-before-save | LOW | Existing MCP `add_task` can be called only from a confirmation handler. | `mcp_client.py` exposes async `add_task`; `streamlit_app.py` already calls it from a form submit handler. | PASS |
| Missing-field follow-up | MEDIUM | Result model can represent either draft or follow-up question without partial `TaskCreate` defaults. | `models.py` has strict `TaskCreate`; implementation can add a wrapper model with nullable draft and required follow-up text. | PASS |
| Regression safety | LOW | Existing tests must pass before implementation. | `uv run pytest` passed: 12 tests passed. | PASS |

## Probes

- Streamlit chat primitive probe: `uv run python -c "import streamlit as st; print(hasattr(st, 'chat_input'), hasattr(st, 'chat_message'))"` returned `True True`.
- Baseline test probe: `uv run pytest` passed with 12 tests.

## Integration Readiness

- The current work can be wired without hidden architecture work: a new `chat_agent.py` can reuse the existing OpenAI settings path, `streamlit_app.py` can add a third tab, and persistence can stay behind `mcp_client.add_task`.

## Verification Readiness

- Automated: `uv run pytest`
- Manual: run `uv run daily-planner-mcp`, run `uv run streamlit run src/daily_planner_agent/streamlit_app.py`, verify complete chat input creates a draft before save, confirm saves through MCP, and incomplete input asks a follow-up question without saving.

## Decision

READY WITH CONSTRAINTS

## Constraints For Implementation

- Do not bypass MCP persistence; confirmed drafts must call existing `mcp_client.add_task`.
- Do not silently default missing required fields; ask a follow-up question.
- Do not introduce live OpenAI calls in automated tests.
- Keep draft state simple enough to survive Streamlit reruns without duplicate saves.

## Approval

Execution approved: no
Implementation may start only after this changes to yes in conversation and
`.khuym/state.json` has `approved_gates.execution = true`.
