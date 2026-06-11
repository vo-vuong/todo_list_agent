# Story Map: Phase 2 - Agent report flow

**Feature slug:** daily-planner-agent
**Phase contract:** `history/daily-planner-agent/phase-2-contract.md`

## Dependency Diagram

Entry -> S1 Runtime config and CLI surface -> S2 MCP client helpers -> S3 PydanticAI planner -> S4 Markdown reporting -> S5 CLI orchestration -> Exit

## Story Table

| Story | Outcome | Contributes To | Creates | Done |
|---|---|---|---|---|
| S1 | Phase 2 settings and CLI entry point exist. | Shared runtime configuration for planner, reporting, and CLI. | `config.py`, `pyproject.toml`, `.env.example`, README command docs. | Config can read MCP URL, OpenAI key/model, and report directory. |
| S2 | MCP client helpers call the running SSE server for today's tasks and completion. | Agent uses MCP instead of direct store access. | `mcp_client.py` or equivalent reusable client module. | Validation proves list and complete calls mutate/read through MCP. |
| S3 | Planner returns a typed schedule from PydanticAI/OpenAI. | Core daily planner behavior. | `planner.py` and schedule result models. | Missing-key path fails early; real-key path returns usable structured output. |
| S4 | Markdown report rendering and dated file writing exist. | Export requirement. | `reporting.py`, `reports/.gitkeep`, report tests. | Rendered markdown has required sections and overflow handling. |
| S5 | CLI runs complete-then-plan flow end to end. | Demo proof for Phase 2 and foundation for Streamlit. | `cli.py`, README validation docs, tests/validation helpers. | CLI writes report and optional completion is visible in MCP-backed data. |

## Story-To-Work-Plan Mapping

| Story | Work Plan Step | Proof |
|---|---|---|
| S1 | Step 1 | Config import check and README command review. |
| S2 | Step 2 | MCP client validation command against a running server. |
| S3 | Steps 3 and 4 | Missing-key test plus real OpenAI validation when `OPENAI_API_KEY` exists. |
| S4 | Step 5 | Report rendering tests and generated markdown inspection. |
| S5 | Step 6 | CLI validation with and without `--complete <task_id>`. |
