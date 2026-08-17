from __future__ import annotations

import hashlib
import json
import random
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from agent.config import CACHE_DIR

SEARCH_BASE = "https://s.jina.ai/"
READER_BASE = "https://r.jina.ai/"

_RATE_LOCK = threading.Lock()
_LAST_CALL = [0.0]


def _politely_space(min_gap_seconds: float = 0.4) -> None:
    with _RATE_LOCK:
        now = time.monotonic()
        wait = _LAST_CALL[0] + min_gap_seconds - now
        if wait > 0:
            time.sleep(wait)
        _LAST_CALL[0] = time.monotonic()


@dataclass
class SearchResult:
    title: str
    url: str
    highlights: str = ""


@dataclass
class FetchedPage:
    url: str
    content: str
    ok: bool = True
    error: str = ""


ENTRY = re.compile(r"^\[(\d+)\]\s+(Title|URL Source|Description|Date):\s?(.*)$")


def parse_search_output(raw: str) -> list[SearchResult]:
    by_index: dict[int, dict[str, str]] = {}
    for line in raw.splitlines():
        match = ENTRY.match(line.strip())
        if match:
            index, field_name, value = int(match.group(1)), match.group(2), match.group(3)
            by_index.setdefault(index, {})[field_name] = value.strip()
    results: list[SearchResult] = []
    for index in sorted(by_index):
        row = by_index[index]
        url = row.get("URL Source", "")
        if url:
            results.append(
                SearchResult(
                    title=row.get("Title", ""),
                    url=url,
                    highlights=row.get("Description", ""),
                )
            )
    return results


@dataclass
class JinaClient:
    api_key: str
    cache_dir: Path = CACHE_DIR
    timeout: int = 90
    max_attempts: int = 6

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, kind: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()[:24]
        return self.cache_dir / f"{kind}-{digest}.json"

    def _get(self, url: str, extra_headers: dict[str, str] | None = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", **(extra_headers or {})}
        last_error = ""
        for attempt in range(self.max_attempts):
            _politely_space()
            request = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body: str = response.read().decode("utf-8", errors="replace")
                    return body
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode(errors="replace")[:300]
                last_error = f"HTTP {exc.code}: {detail}"
                if exc.code == 429 or exc.code >= 500:
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    delay = float(retry_after) if retry_after else min(2**attempt * 5, 60)
                    time.sleep(delay + random.random())
                    continue
                raise RuntimeError(f"jina GET {url} failed: {last_error}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = str(exc)[:300]
                time.sleep(min(2**attempt * 5, 60) + random.random())
        raise RuntimeError(f"jina GET {url} failed after retries: {last_error}")

    def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        cache_path = self._cache_path("search", f"{query}|{num_results}")
        if cache_path.exists():
            payload = json.loads(cache_path.read_text())
            return [SearchResult(**row) for row in payload]
        url = SEARCH_BASE + "?" + urllib.parse.urlencode({"q": query})
        raw = self._get(url, {"X-Respond-With": "no-content"})
        results = parse_search_output(raw)[:num_results]
        cache_path.write_text(json.dumps([r.__dict__ for r in results], indent=1))
        return results

    def fetch(self, url: str) -> FetchedPage:
        cache_path = self._cache_path("fetch", url)
        if cache_path.exists():
            payload = json.loads(cache_path.read_text())
            return FetchedPage(**payload)
        try:
            raw = self._get(READER_BASE + url)
            page = FetchedPage(url=url, content=raw, ok=True)
        except (RuntimeError, OSError) as exc:
            page = FetchedPage(url=url, content="", ok=False, error=str(exc)[:300])
        cache_path.write_text(json.dumps(page.__dict__, indent=1))
        return page
