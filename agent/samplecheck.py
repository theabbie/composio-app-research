from __future__ import annotations

import json
from collections import defaultdict

from agent.config import APPS_JSON, VERIFICATION_DIR
from agent.research import load_seeds
from agent.schemas import HumanCheck

SAMPLE_PATH = VERIFICATION_DIR / "human_sample.json"
SUMMARY_PATH = VERIFICATION_DIR / "summary.json"
CHECKED_FIELDS = ["one_liner", "auth_methods", "access", "api_surface", "verdict"]
SAMPLE_PER_CATEGORY = 2


def make_sample() -> list[HumanCheck]:
    seeds = load_seeds(APPS_JSON)
    by_category: dict[str, list[int]] = defaultdict(list)
    for seed in seeds:
        by_category[seed.category].append(seed.id)
    sample: list[HumanCheck] = []
    for category in sorted(by_category):
        ids = sorted(by_category[category])
        step = max(1, len(ids) // SAMPLE_PER_CATEGORY)
        chosen = sorted({ids[0], ids[-1]} | set(ids[::step]))[:SAMPLE_PER_CATEGORY]
        for app_id in chosen:
            seed = next(s for s in seeds if s.id == app_id)
            sample.append(HumanCheck(app_id=app_id, app=seed.app))
    return sample


def accuracy(checks: list[HumanCheck], key: str) -> dict[str, float]:
    per_field: dict[str, list[bool]] = {name: [] for name in CHECKED_FIELDS}
    overall: list[bool] = []
    for check in checks:
        results: dict[str, bool] = getattr(check, key)
        if not results:
            continue
        for name in CHECKED_FIELDS:
            if name in results:
                per_field[name].append(results[name])
        overall.append(all(results.get(name, False) for name in CHECKED_FIELDS))
    summary = {
        name: (sum(values) / len(values) if values else 0.0) for name, values in per_field.items()
    }
    summary["all_fields_correct"] = sum(overall) / len(overall) if overall else 0.0
    summary["apps_scored"] = float(len(overall))
    return summary


def run_sample_check() -> int:
    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_PATH.exists():
        sample = make_sample()
        SAMPLE_PATH.write_text(
            json.dumps([s.model_dump() for s in sample], indent=1) + "\n"
        )
        print(
            f"wrote sample template -> {SAMPLE_PATH}\n"
            "fill in fields_correct_pass1/fields_correct_pass2 after hand-checking, "
            "then re-run `agent sample-check`"
        )
        return 0
    checks = [HumanCheck.model_validate(row) for row in json.loads(SAMPLE_PATH.read_text())]
    pass1 = accuracy(checks, "fields_correct_pass1")
    pass2 = accuracy(checks, "fields_correct_pass2")
    summary = {"sample_size": len(checks), "pass1": pass1, "pass2": pass2}
    SUMMARY_PATH.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0
