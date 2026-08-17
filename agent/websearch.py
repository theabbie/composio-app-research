from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agent.config import CACHE_DIR


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


@dataclass
class ExaClient:
    exa_bin: str = "exa"
    cache_dir: Path = CACHE_DIR
    timeout: int = 120

    def __post_init__(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, kind: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()[:24]
        return self.cache_dir / f"{kind}-{digest}.json"

    def _run(self, args: list[str]) -> str:
        proc = subprocess.run(
            [self.exa_bin, *args],
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"exa {' '.join(args)} failed: {proc.stderr[:500]}")
        return proc.stdout

    def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        cache_path = self._cache_path("search", f"{query}|{num_results}")
        if cache_path.exists():
            payload = json.loads(cache_path.read_text())
            return [SearchResult(**row) for row in payload]
        raw = self._run(["search", query, str(num_results)])
        results = parse_search_output(raw)
        cache_path.write_text(json.dumps([r.__dict__ for r in results], indent=1))
        return results

    def fetch(self, url: str) -> FetchedPage:
        cache_path = self._cache_path("fetch", url)
        if cache_path.exists():
            payload = json.loads(cache_path.read_text())
            return FetchedPage(**payload)
        try:
            raw = self._run(["fetch", url])
            page = FetchedPage(url=url, content=raw, ok=True)
        except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
            page = FetchedPage(url=url, content="", ok=False, error=str(exc)[:300])
        cache_path.write_text(json.dumps(page.__dict__, indent=1))
        return page


BLOCK_SPLIT = re.compile(r"\n---\n+")
FIELD = re.compile(r"^(Title|URL|Published|Author|Highlights):\s?(.*)$")


def parse_search_output(raw: str) -> list[SearchResult]:
    results: list[SearchResult] = []
    for block in BLOCK_SPLIT.split(raw):
        title, url, highlights = "", "", ""
        lines = block.splitlines()
        index = 0
        while index < len(lines):
            match = FIELD.match(lines[index])
            if match:
                name, value = match.group(1), match.group(2)
                if name == "Title":
                    title = value.strip()
                elif name == "URL":
                    url = value.strip()
                elif name == "Highlights":
                    highlights = "\n".join([value, *lines[index + 1 :]]).strip()
                    index = len(lines)
            index += 1
        if url:
            results.append(SearchResult(title=title, url=url, highlights=highlights))
    return results
