from __future__ import annotations

import json
import re
from pathlib import Path

from agent.schemas import AppSeed

CATEGORY_HEADING = re.compile(r"^####\s+(\d+)\\\.\s+(.+?)\s*$")
LINK_CELL = re.compile(r"\[([^\]]+)\]\(([^)]+)\)\s*(.*)")
PAREN_HINT = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*$")

EXPECTED_COUNT = 100


def parse_assignment(markdown: str) -> list[AppSeed]:
    line_category: list[str] = []
    current = ""
    for line in markdown.splitlines():
        match = CATEGORY_HEADING.match(line)
        if match:
            current = match.group(2).strip()
        line_category.append(current)

    cells: list[tuple[str, str]] = []
    for line_index, line in enumerate(markdown.splitlines()):
        for piece in line.split("|"):
            stripped = piece.strip()
            if stripped:
                cells.append((stripped, line_category[line_index]))

    seeds: list[AppSeed] = []
    cursor = 0
    while cursor < len(cells):
        text, cell_category = cells[cursor]
        if re.fullmatch(r"\d{1,3}", text) and 1 <= int(text) <= EXPECTED_COUNT:
            if cursor + 2 >= len(cells):
                break
            app_name = cells[cursor + 1][0]
            website_cell = cells[cursor + 2][0]
            link = LINK_CELL.match(website_cell)
            if link:
                domain, url, hint = link.group(1), link.group(2), link.group(3).strip()
            else:
                domain, url, hint = website_cell, "", ""
                paren = PAREN_HINT.match(domain)
                if paren and " " not in paren.group(1):
                    domain, hint = paren.group(1), paren.group(2)
            hint = hint.strip("() ")
            seeds.append(
                AppSeed(
                    id=int(text),
                    app=app_name,
                    category=cell_category,
                    domain=domain,
                    url=url,
                    hint=hint,
                )
            )
            cursor += 3
            continue
        cursor += 1

    ids = [seed.id for seed in seeds]
    if len(seeds) != EXPECTED_COUNT or sorted(ids) != list(range(1, EXPECTED_COUNT + 1)):
        raise ValueError(
            f"expected ids 1..{EXPECTED_COUNT}, got {len(seeds)} rows; "
            f"missing: {sorted(set(range(1, EXPECTED_COUNT + 1)) - set(ids))}"
        )
    return seeds


def write_seed(markdown_path: Path, out_path: Path) -> list[AppSeed]:
    seeds = parse_assignment(markdown_path.read_text())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps([s.model_dump() for s in seeds], indent=2) + "\n")
    return seeds
