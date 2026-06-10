from __future__ import annotations

from datetime import date

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

from daily_planner_agent.config import OpenAISettings, get_openai_settings
from daily_planner_agent.models import DailyPlan, Task


class MissingOpenAIKeyError(RuntimeError):
    """Raised when LLM planning is requested without an API key."""


PLANNER_INSTRUCTIONS = """
You are a daily planning agent. Produce a practical schedule from the provided
tasks and return only the structured output requested by the application.

Rules:
- Use only tasks from the input.
- Do not change stored task priority values.
- Schedule inside the local workday from 09:00 to 17:00.
- Do not schedule anything from 12:00 to 13:00.
- Prefer high priority tasks, then medium, then low, while considering due dates
  and estimated minutes.
- Tasks that do not fit must go in unscheduled_overflow with a concise reason.
- Use 24-hour local times.
""".strip()


async def generate_daily_plan(tasks: list[Task], *, plan_date: date | None = None) -> DailyPlan:
    settings = require_openai_api_key()
    target_date = plan_date or date.today()
    model = OpenAIResponsesModel(
        settings.model,
        provider=OpenAIProvider(api_key=settings.api_key),
    )
    agent = Agent(
        model,
        output_type=DailyPlan,
        instructions=PLANNER_INSTRUCTIONS,
        retries=2,
    )
    result = await agent.run(_build_prompt(tasks, target_date))
    return result.output


def require_openai_api_key() -> OpenAISettings:
    settings = get_openai_settings()
    if settings.api_key is None:
        raise MissingOpenAIKeyError(
            "OPENAI_API_KEY is required for LLM planning. Add it to .env before running the planner."
        )
    return settings


def _build_prompt(tasks: list[Task], plan_date: date) -> str:
    task_lines = [
        (
            f"- id={task.id}; title={task.title}; description={task.description}; "
            f"due_date={task.due_date.isoformat()}; estimated_minutes={task.estimated_minutes}; "
            f"priority={task.priority}; completed={task.completed}"
        )
        for task in tasks
    ]
    task_text = "\n".join(task_lines) if task_lines else "- No due or overdue incomplete tasks."
    return f"""
Create a daily plan for {plan_date.isoformat()}.

Today's MCP tasks:
{task_text}

Return a DailyPlan with:
- plan_date: {plan_date.isoformat()}
- summary: one concise paragraph
- time_blocks: scheduled tasks only
- unscheduled_overflow: tasks that do not fit
""".strip()
