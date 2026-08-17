from __future__ import annotations

import json
from pathlib import Path

from agent.config import RESEARCH_DIR, VERIFICATION_DIR
from agent.research import run_research
from agent.schemas import AutoVerification, FlagSeverity


def flagged_feedback(
    verification_path: Path,
) -> dict[int, str]:
    rows = json.loads(verification_path.read_text())
    feedback: dict[int, str] = {}
    for row in rows:
        verification = AutoVerification.model_validate(row)
        errors = [f for f in verification.flags if f.severity == FlagSeverity.ERROR]
        if errors:
            feedback[verification.app_id] = "\n".join(f"- {f.field}: {f.detail}" for f in errors)
    return feedback


def run_repair(directory: Path = RESEARCH_DIR) -> int:
    verification_path = VERIFICATION_DIR / "auto-pass1.json"
    if not verification_path.exists():
        print("run `agent verify` first")
        return 1
    feedback = flagged_feedback(verification_path)
    if not feedback:
        print("no flagged apps; nothing to repair")
        return 0
    print(f"repairing {len(feedback)} flagged apps as pass 2")
    return run_research(
        only=sorted(feedback),
        force=True,
        pass_number=2,
        directory=directory,
        feedback_by_id=feedback,
    )
