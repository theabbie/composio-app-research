from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.config import CACHE_DIR, Settings

USAGE_LOG = CACHE_DIR / "llm_usage.jsonl"
_usage_lock = threading.Lock()


@dataclass
class ChatResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float


class LLMError(RuntimeError):
    pass


class ChatClient:
    def __init__(self, settings: Settings, timeout: int = 300, max_retries: int = 3):
        self.base_url = settings.llm_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.timeout = timeout
        self.max_retries = max_retries

    def chat(
        self,
        system: str,
        user: str,
        max_tokens: int = 8192,
        purpose: str = "extract",
    ) -> ChatResponse:
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        body = json.dumps(payload).encode()
        last_error = ""
        for attempt in range(self.max_retries):
            request = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data: dict[str, Any] = json.loads(response.read().decode())
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode()[:300]
                last_error = f"HTTP {exc.code}: {detail}"
                if exc.code in (429, 500, 502, 503, 504):
                    time.sleep(2**attempt * 5)
                    continue
                raise LLMError(last_error) from exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = str(exc)[:300]
                time.sleep(2**attempt * 5)
        else:
            raise LLMError(f"chat failed after {self.max_retries} attempts: {last_error}")

        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        if not content.strip():
            reasoning = message.get("reasoning_content") or ""
            try:
                parsed = extract_json_object(reasoning)
                content = json.dumps(parsed)
            except LLMError:
                content = ""
        usage = data.get("usage", {})
        result = ChatResponse(
            content=content,
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            cost_usd=float(usage.get("cost", 0.0)),
        )
        with _usage_lock:
            USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
            with USAGE_LOG.open("a") as handle:
                handle.write(
                    json.dumps(
                        {
                            "ts": time.time(),
                            "purpose": purpose,
                            "model": self.model,
                            "prompt_tokens": result.prompt_tokens,
                            "completion_tokens": result.completion_tokens,
                            "cost_usd": result.cost_usd,
                        }
                    )
                    + "\n"
                )
        return result


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    if start == -1:
        raise LLMError(f"no JSON object in model output: {text[:200]!r}")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    parsed: dict[str, Any] = json.loads(text[start : index + 1])
                except json.JSONDecodeError as exc:
                    raise LLMError(f"invalid JSON in model output: {exc}") from exc
                return parsed
    raise LLMError(f"unbalanced JSON in model output: {text[:200]!r}")


def load_usage(path: Path = USAGE_LOG) -> dict[str, Any]:
    if not path.exists():
        return {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
    calls = prompt = completion = 0
    cost = 0.0
    by_purpose: dict[str, int] = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        calls += 1
        prompt += row["prompt_tokens"]
        completion += row["completion_tokens"]
        cost += row["cost_usd"]
        by_purpose[row["purpose"]] = by_purpose.get(row["purpose"], 0) + 1
    return {
        "calls": calls,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "cost_usd": round(cost, 4),
        "by_purpose": by_purpose,
    }
