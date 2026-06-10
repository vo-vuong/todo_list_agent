from __future__ import annotations

import argparse
import anyio

from daily_planner_agent.mcp_client import McpClientError, complete_task, list_todays_tasks
from daily_planner_agent.planner import MissingOpenAIKeyError, generate_daily_plan, require_openai_api_key
from daily_planner_agent.reporting import write_markdown_report


async def run_plan(*, complete_task_id: str | None = None) -> int:
    require_openai_api_key()

    if complete_task_id:
        completed = await complete_task(complete_task_id)
        print(f"completed_task={completed.id}")

    tasks = await list_todays_tasks()
    print(f"todays_task_count={len(tasks)}")

    plan = await generate_daily_plan(tasks)
    report_path = write_markdown_report(plan)
    print(f"report_path={report_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a daily planner markdown report.")
    parser.add_argument(
        "--complete",
        metavar="TASK_ID",
        help="Complete a task through MCP before generating the daily plan.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(anyio.run(_run_from_args, args.complete))
    except MissingOpenAIKeyError as exc:
        parser.exit(2, f"error: {exc}\n")
    except McpClientError as exc:
        parser.exit(3, f"error: {exc}\n")


async def _run_from_args(complete_task_id: str | None) -> int:
    return await run_plan(complete_task_id=complete_task_id)


if __name__ == "__main__":
    main()
