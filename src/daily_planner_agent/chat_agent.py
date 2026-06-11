from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_ai import Agent
from pydantic_ai.mcp import CallToolFunc, MCPToolset
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from daily_planner_agent.config import get_mcp_server_settings
from daily_planner_agent.mcp_client import discover_tools
from daily_planner_agent.models import Priority, TaskCreate
from daily_planner_agent.planner import require_openai_api_key

ChatRole = Literal["user", "assistant"]
RequiredTaskField = Literal["title", "due_date", "estimated_minutes", "priority"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: ChatRole
    content: str = Field(min_length=1)


class TaskDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = ""
    due_date: date
    estimated_minutes: int = Field(gt=0)
    priority: Priority

    def to_task_create(self) -> TaskCreate:
        return TaskCreate(
            title=self.title,
            description=self.description,
            due_date=self.due_date,
            estimated_minutes=self.estimated_minutes,
            priority=self.priority,
        )


class ChatTaskResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft: TaskDraft | None = None
    follow_up_question: str | None = None
    missing_fields: list[RequiredTaskField] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_result_shape(self) -> "ChatTaskResult":
        has_draft = self.draft is not None
        has_follow_up = self.follow_up_question is not None and self.follow_up_question.strip() != ""
        if has_draft == has_follow_up:
            raise ValueError("Return exactly one of draft or follow_up_question.")
        if has_draft and self.missing_fields:
            raise ValueError("Complete drafts must not include missing_fields.")
        if has_follow_up and not self.missing_fields:
            raise ValueError("Follow-up questions must include missing_fields.")
        return self


class ChatToolCallTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_summary: str


class ChatActionTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    discovered_tools: list[str] = Field(default_factory=list)
    calls: list[ChatToolCallTrace] = Field(default_factory=list)


class ChatActionAgentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)


class ChatActionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)
    trace: ChatActionTrace


CHAT_TASK_INSTRUCTIONS = """
You help create one task from a short chat conversation.

Return structured output only.

Required fields for a complete draft:
- title
- due_date
- estimated_minutes
- priority: one of low, medium, high

Rules:
- If any required field is missing or ambiguous, do not create a draft. Ask one
  concise follow-up question and list the missing fields.
- Do not silently choose default values for required fields.
- Description is optional. Use an empty string when the user gives no useful
  description.
- Convert relative dates using the provided current local date.
- Preserve user intent. Do not invent details that are not in the conversation.
""".strip()


CHAT_ACTION_INSTRUCTIONS = """
You execute user task-management actions by using only MCP tools provided to you.

Rules:
- Use the discovered MCP tools to complete tasks and generate markdown reports.
- Do not claim an action succeeded unless the relevant MCP tool returns success.
- For task completion, prefer a tool that accepts a task reference when available.
  Pass the exact task ID or task title from the user as the reference.
- If an MCP tool reports that a task title is ambiguous, ask the user which task
  ID to use and do not call another completion tool.
- If the user asks for multiple actions, call the needed MCP tools in order.
- Return a concise user-facing message summarizing what happened.
""".strip()


ACTION_KEYWORDS = (
    "complete",
    "completed",
    "finish",
    "done",
    "mark",
    "hoan thanh",
    "hoàn thành",
    "xong",
    "export",
    "report",
    "markdown",
    "daily plan",
    "plan markdown",
    "xuat",
    "xuất",
    "bao cao",
    "báo cáo",
    "ke hoach",
    "kế hoạch",
)


async def draft_task_from_chat(
    messages: list[ChatMessage],
    *,
    today: date | None = None,
) -> ChatTaskResult:
    settings = require_openai_api_key()
    model = OpenAIResponsesModel(
        settings.model,
        provider=OpenAIProvider(api_key=settings.api_key),
    )
    agent = Agent(
        model,
        output_type=ChatTaskResult,
        instructions=CHAT_TASK_INSTRUCTIONS,
        retries=2,
    )
    result = await agent.run(_build_chat_prompt(messages, today or date.today()))
    return result.output


async def run_chat_action_from_chat(
    messages: list[ChatMessage],
    *,
    today: date | None = None,
) -> ChatActionResult:
    settings = require_openai_api_key()
    mcp_settings = get_mcp_server_settings()
    discovered = await discover_tools()
    trace = ChatActionTrace(discovered_tools=[tool.name for tool in discovered])

    model = OpenAIResponsesModel(
        settings.model,
        provider=OpenAIProvider(api_key=settings.api_key),
    )
    toolset = MCPToolset(
        mcp_settings.url,
        process_tool_call=_build_process_tool_call(trace),
        cache_tools=False,
    )
    agent = Agent(
        model,
        output_type=ChatActionAgentOutput,
        instructions=CHAT_ACTION_INSTRUCTIONS,
        toolsets=[toolset],
        retries=2,
    )
    result = await agent.run(_build_action_prompt(messages, today or date.today(), trace.discovered_tools))
    return ChatActionResult(message=result.output.message, trace=trace)


def looks_like_action_request(content: str) -> bool:
    normalized = content.casefold()
    return any(keyword in normalized for keyword in ACTION_KEYWORDS)


def _build_chat_prompt(messages: list[ChatMessage], today: date) -> str:
    lines = [f"Current local date: {today.isoformat()}", "", "Conversation:"]
    for message in messages:
        lines.append(f"{message.role}: {message.content}")
    lines.extend(
        [
            "",
            "Create a complete task draft only if title, due_date, estimated_minutes, and priority are all clear.",
            "Otherwise ask for the missing information.",
        ]
    )
    return "\n".join(lines)


def _build_action_prompt(messages: list[ChatMessage], today: date, discovered_tools: list[str]) -> str:
    lines = [
        f"Current local date: {today.isoformat()}",
        "Discovered MCP tools:",
        *[f"- {tool}" for tool in discovered_tools],
        "",
        "Conversation:",
    ]
    for message in messages:
        lines.append(f"{message.role}: {message.content}")
    lines.extend(
        [
            "",
            "Use the MCP tools to satisfy the latest user action request.",
            "If no discovered tool can satisfy the request, say what is missing.",
        ]
    )
    return "\n".join(lines)


def _build_process_tool_call(trace: ChatActionTrace):
    async def process_tool_call(_ctx: object, call_tool: CallToolFunc, tool_name: str, arguments: dict[str, Any]):
        result = await call_tool(tool_name, arguments)
        trace.calls.append(
            ChatToolCallTrace(
                tool_name=tool_name,
                arguments=dict(arguments),
                result_summary=summarize_tool_result(result),
            )
        )
        return result

    return process_tool_call


def summarize_tool_result(result: object) -> str:
    if isinstance(result, dict):
        message = result.get("message")
        status = result.get("status")
        if isinstance(message, str) and isinstance(status, str):
            return f"{status}: {message}"
        if isinstance(message, str):
            return message
        if isinstance(status, str):
            return status
    if isinstance(result, list):
        return f"Returned {len(result)} item(s)."
    text = str(result)
    if len(text) > 180:
        return text[:177] + "..."
    return text
