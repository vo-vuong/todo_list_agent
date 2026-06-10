from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

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
