from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="agent", description="Composio 100-app research pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    seed_p = sub.add_parser("seed", help="parse the assignment markdown into data/apps.json")
    seed_p.add_argument("markdown", nargs="?", default="composioassignment.md")
    seed_p.add_argument("--out", default=None)

    research_p = sub.add_parser("research", help="run the research agent over the seed set")
    research_p.add_argument("--only", type=int, nargs="*", default=None)
    research_p.add_argument("--limit", type=int, default=None)
    research_p.add_argument("--force", action="store_true")
    research_p.add_argument("--concurrency", type=int, default=4)

    sub.add_parser("verify", help="re-fetch evidence URLs and check quoted claims")
    sub.add_parser("repair", help="re-research apps flagged by verification")
    sub.add_parser("sample-check", help="score the human-checked sample")
    sub.add_parser("analyze", help="aggregate results into pattern analysis JSON")

    args = parser.parse_args()

    if args.command == "seed":
        from agent.config import APPS_JSON
        from agent.seed import write_seed

        out = Path(args.out) if args.out else APPS_JSON
        seeds = write_seed(Path(args.markdown), out)
        print(f"wrote {len(seeds)} apps -> {out}")
        return 0

    if args.command == "research":
        from agent.research import run_research

        return run_research(
            only=args.only, limit=args.limit, force=args.force, concurrency=args.concurrency
        )

    if args.command == "verify":
        from agent.verify import run_verify

        return run_verify()

    if args.command == "repair":
        from agent.repair import run_repair

        return run_repair()

    if args.command == "sample-check":
        from agent.samplecheck import run_sample_check

        return run_sample_check()

    if args.command == "analyze":
        from agent.analyze import run_analyze

        return run_analyze()

    return 2


if __name__ == "__main__":
    sys.exit(main())
