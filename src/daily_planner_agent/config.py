from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
TASKS_PATH = DATA_DIR / "tasks.json"
SAMPLE_TASKS_PATH = DATA_DIR / "tasks.sample.json"
DEFAULT_MCP_SERVER_URL = "http://localhost:8000/sse"
DEFAULT_OPENAI_MODEL = "gpt-5-nano"


@dataclass(frozen=True)
class McpServerSettings:
    url: str
    host: str
    port: int
    sse_path: str


@dataclass(frozen=True)
class OpenAISettings:
    api_key: str | None
    model: str


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def get_mcp_server_settings() -> McpServerSettings:
    load_environment()
    url = os.getenv("MCP_SERVER_URL", DEFAULT_MCP_SERVER_URL)
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8000
    sse_path = parsed.path or "/sse"
    return McpServerSettings(url=url, host=host, port=port, sse_path=sse_path)


def get_openai_settings() -> OpenAISettings:
    load_environment()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is not None:
        api_key = api_key.strip() or None
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL
    return OpenAISettings(api_key=api_key, model=model)


def report_path_for_date(plan_date: str) -> Path:
    return REPORTS_DIR / f"daily-plan-{plan_date}.md"
