from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
APPS_JSON = DATA_DIR / "apps.json"
RESEARCH_DIR = DATA_DIR / "research"
VERIFICATION_DIR = DATA_DIR / "verification"
CACHE_DIR = DATA_DIR / "cache"

DEFAULT_BASE_URL = "https://compute.virtuals.io/v1"
DEFAULT_MODEL = "moonshotai-kimi-k3"
DEFAULT_KEY_CMD = "security find-generic-password -a cabhishek -s pi-virtuals-compute -w"


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    jina_api_key: str


def resolve_api_key() -> str:
    key = os.environ.get("LLM_API_KEY", "").strip()
    if key:
        return key
    cmd = os.environ.get("LLM_API_KEY_CMD", DEFAULT_KEY_CMD)
    try:
        result = subprocess.run(
            shlex.split(cmd), capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result and result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    raise RuntimeError(
        "No LLM API key available. Set LLM_API_KEY in the environment or .env "
        "(see .env.example), or configure LLM_API_KEY_CMD to a command that prints one."
    )


def get_settings() -> Settings:
    load_dotenv()
    jina_key = os.environ.get("JINA_API_KEY", "").strip()
    if not jina_key:
        raise RuntimeError(
            "JINA_API_KEY is not set. Add it to .env (see .env.example) or the environment."
        )
    return Settings(
        llm_base_url=os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        llm_api_key=resolve_api_key(),
        llm_model=os.environ.get("LLM_MODEL", DEFAULT_MODEL),
        jina_api_key=jina_key,
    )
