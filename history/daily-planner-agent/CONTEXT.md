# Daily Planner Agent - Context

**Feature slug:** daily-planner-agent
**Date:** 2026-06-10
**Clarification status:** complete
**Scope:** Standard
**Domain types:** SEE | CALL | RUN | READ | ORGANIZE

## Feature Boundary

Build a small Python Streamlit demo where a daily planner agent uses MCP tools backed by a local JSON task store to list, add, and complete tasks, then produces a prioritized, time-blocked daily schedule as a markdown report.

## Locked Decisions

These are fixed. Implementation must follow them exactly.

- **D1:** The demo uses Python plus a real LLM call; the agent calls OpenAI to prioritize and time-block tasks while the MCP server wraps a local JSON task store.
  - Rationale: This changes the runtime, dependencies, configuration, and fallback behavior compared with an offline rule-based demo.
- **D2:** The local JSON task store uses a planner-ready schema: `id`, `title`, `description`, `due_date`, `estimated_minutes`, `priority`, and `completed`.
  - Rationale: The planner needs enough task metadata to produce useful prioritization and time blocks without expanding into extra demo complexity.
- **D3:** The demo exports only a markdown report, written to a dated file such as `reports/daily-plan-YYYY-MM-DD.md`; notifications are out of scope.
  - Rationale: This keeps the output deterministic and easy to validate in a local demo.
- **D4:** `complete_task` is demonstrated through a CLI argument: the user runs the agent with `--complete <task_id>`, and the agent calls the MCP `complete_task` tool for that task before producing the daily plan.
  - Rationale: This proves the agent can act through MCP while keeping task completion explicit and user-controlled.
- **D5:** The demo includes a Streamlit UI as the primary interface for viewing tasks, adding tasks, completing a selected task, generating the daily plan, and displaying the markdown report.
  - Rationale: Streamlit keeps the UI simple while making the demo easier to inspect than a CLI-only flow.
- **D6:** The Python agent layer uses PydanticAI with OpenAI as the model provider.
  - Rationale: This gives the demo a typed agent framework while preserving the requirement that the agent uses a real OpenAI LLM call.
- **D7:** The MCP server uses the official MCP Python SDK with FastMCP, imported from `mcp.server.fastmcp`.
  - Rationale: This keeps the MCP implementation close to the official Python SDK while still using the concise FastMCP tool-decorator style.
- **D8:** The MCP server runs as a separate HTTP/SSE process, and the Streamlit/PydanticAI app connects to it by URL.
  - Rationale: This makes the MCP boundary explicit and closer to a real client-server demo, at the cost of requiring two local run commands.
- **D9:** Runtime configuration is loaded from a local `.env` file. `OPENAI_MODEL` defaults to `gpt-5-nano`, and `OPENAI_API_KEY` is required for LLM planning. If the key is missing, the Streamlit UI must show a clear error and must not generate an LLM plan.
  - Rationale: This keeps the demo aligned with the requested model while making missing credential failure explicit in the UI.
- **D10:** "Today's tasks" means incomplete tasks with `due_date` on or before today's local date, including overdue tasks and tasks due today.
  - Rationale: This keeps the planner focused on urgent work while excluding future and completed tasks.
- **D11:** The planner schedules within a fixed local workday from 09:00 to 17:00, with lunch blocked from 12:00 to 13:00. Tasks that do not fit in the available time must be listed under `Unscheduled overflow`.
  - Rationale: This makes generated schedules predictable, realistic, and easy to validate.
- **D12:** Task `priority` accepts only `low`, `medium`, or `high`. The LLM may reorder tasks in the schedule but must not modify the stored priority value.
  - Rationale: This keeps task data stable while still allowing the planner to use reasoning for ordering.
- **D13:** Markdown reports use a concise format with title/date, summary, time-block table, and `Unscheduled overflow` list. MCP tool-call evidence is not required inside the report.
  - Rationale: This keeps the report easy to read while leaving MCP evidence to logs, UI status, or validation output.
- **D14:** The Streamlit UI uses two tabs: `Tasks` for listing, adding, and completing tasks, and `Planner` for generating, previewing, and downloading the markdown report.
  - Rationale: This separates task-store actions from planning output without adding a debug-heavy interface.
- **D15:** The project uses `uv` with `pyproject.toml`; setup and run instructions must use `uv sync` and `uv run ...`.
  - Rationale: This keeps dependency management modern, repeatable, and concise for the demo.
- **D16:** The repo ships with `data/tasks.json` containing sample tasks. The app and MCP tools mutate that file directly, and the demo must include a reset button or command that restores sample data.
  - Rationale: This makes the demo immediately runnable while still allowing repeatable reset after task mutations.

## Specific Ideas And References

- User requirement: "Create a daily planner agent."
- User requirement: "Stake today's tasks (fetched via MCP) and produce a prioritized, time-blocked schedule."
- User requirement: "Export as a markdown report or fire a notification."
- User requirement: "Build an MCP server: Wrap the task store. Expose list_tasks, add_task, complete_task."
- User requirement: "MCP wraps local JSON. Agent call list & complete."
- User clarification: "UI là streamlit cho đơn giản."
- User selected PydanticAI as the Python agent library.
- User selected official MCP Python SDK with FastMCP as the MCP server library.
- User selected `gpt-5-nano` as the OpenAI model and requested `.env` configuration with a Streamlit UI error when the API key is missing.
- PydanticAI docs checked: `https://pydantic.dev/docs/ai/mcp/overview/` says PydanticAI can connect to MCP servers directly, via FastMCP Client, or through provider-native MCP tools.
- PydanticAI docs checked: `https://pydantic.dev/docs/ai/mcp/client/` lists `MCPServerStdio`, `MCPServerSSE`, and `MCPServerStreamableHTTP` as client connection options.
- MCP Python SDK docs checked: `https://github.com/modelcontextprotocol/python-sdk` describes building MCP servers/clients with stdio, SSE, and Streamable HTTP transports.

## Existing Code Context

This is a new project. No implementation files have been scouted yet.

## Validation

- Run the Python demo successfully against a local JSON task store.
- Run the Streamlit UI and use it to view tasks, add a task, complete a task, and generate the report.
- Show that the agent calls MCP `list_tasks` and can call `complete_task`.
- Produce a markdown daily schedule report containing prioritized tasks and time blocks.

## Open Questions

No open questions block implementation.

## Deferred Ideas

- Advanced UI features such as authentication, multi-user support, drag-and-drop scheduling, and persistent browser sessions - deferred because Streamlit should remain a small local demo interface.
- Real desktop, email, or webhook notification - deferred because the selected output is markdown report only.
- Single-process embedded MCP server mode - deferred because the selected topology is a separate HTTP/SSE MCP server process.

## Handoff Note

CONTEXT.md is the source of truth. Decision IDs are stable. Implementation must
honor locked decisions, preserve listed patterns, and satisfy validation proof
before claiming done.
