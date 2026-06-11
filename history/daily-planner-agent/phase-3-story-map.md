# Story Map: Phase 3 - Streamlit Demo Interface

**Feature slug:** daily-planner-agent
**Phase contract:** `history/daily-planner-agent/phase-3-contract.md`

## Dependency Diagram

Entry -> S1 UI shell -> S2 Task actions -> S3 Planner report flow -> S4 Docs and validation -> Exit

## Story Table

| Story | Outcome | Contributes To | Creates | Done |
|---|---|---|---|---|
| S1 | Streamlit can launch the demo and render the required `Tasks` and `Planner` tabs. | Phase exit state for primary UI availability. | Streamlit dependency, script/command, `src/daily_planner_agent/streamlit_app.py` shell. | App starts locally and renders both tabs. |
| S2 | The `Tasks` tab performs task list, add, complete, and reset through MCP. | Phase exit state for task-store actions in UI. | MCP client helpers for list/add/reset as needed, task table/form/select/reset UI. | Manual UI flow mutates `data/tasks.json` through the running MCP server. |
| S3 | The `Planner` tab generates, previews, writes, and downloads the markdown report. | Phase exit state for LLM-backed report generation in UI. | Planner action UI, missing-key error path, report preview, download button. | Real-key UI run writes `reports/daily-plan-YYYY-MM-DD.md`; missing-key run shows a clear error. |
| S4 | README and tests match the final demo shape. | Review readiness and repeatable validation. | README Streamlit instructions and focused tests for helper/report/UI-safe logic. | `uv run pytest` passes and README no longer describes Streamlit as deferred. |

## Story-To-Work-Plan Mapping

| Story | Work Plan Step | Proof |
|---|---|---|
| S1 | Step 1 | `uv run streamlit ...` starts and shows two tabs. |
| S2 | Steps 2-3 | UI task actions update the visible list and underlying JSON through MCP. |
| S3 | Steps 4-5 | Planner tab writes/previews/downloads markdown and blocks missing-key planning. |
| S4 | Steps 6-7 | README has final commands and `uv run pytest` passes. |
