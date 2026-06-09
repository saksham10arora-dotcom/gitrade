"""
settle.py -- Sunday 00:00 UTC settlement job.

Cash-settles all positions to real GitHub numbers.
Posts a champion issue. Resets the week.
"""

from __future__ import annotations
import json
import os
import time
from pathlib import Path

from github import Github, Auth

from engine import settle_week
from github_stats import fetch_real_stats

STATE_FILE = Path("state.json")
REPO_NAME  = os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")
TOKEN      = os.environ.get("GITHUB_TOKEN", "")


def run_settlement():
    if not STATE_FILE.exists():
        print("No state.json found. Skipping settlement.")
        return

    state = json.loads(STATE_FILE.read_text())
    real_stats = fetch_real_stats(REPO_NAME, fallback=state.get("fair_value", {}))

    summary = settle_week(state, real_stats)

    # Post champion issue
    if TOKEN:
        g = Github(auth=Auth.Token(TOKEN))
        repo = g.get_repo(REPO_NAME)

        lines = [f"## Week {state.get('week_number', '?') - 1} Settlement\n",
                 f"Real stats: STAR={real_stats.get('STAR')} COMMIT={real_stats.get('COMMIT')} FORK={real_stats.get('FORK')}\n",
                 "\n### Results\n",
                 "| Trader | P&L |",
                 "|--------|-----|"]

        for name, data in sorted(summary.items(), key=lambda x: -x[1]["pnl"]):
            sign = "+" if data["pnl"] >= 0 else ""
            lines.append(f"| {name} | {sign}{data['pnl']:.0f} |")

        hall = state.get("hall_of_fame", [])
        if hall:
            last = hall[-2:]  # human + bot champion
            champions = [f"{e['name']} ({e['league']}, +{e['pnl']:.0f})" for e in last]
            lines.append(f"\nChampions: {', '.join(champions)}")

        repo.create_issue(
            title=f"Settlement: Week {state.get('week_number', 1) - 1}",
            body="\n".join(lines),
            labels=[],
        )

    STATE_FILE.write_text(json.dumps(state, indent=2))
    print(f"Settlement complete. Real stats: {real_stats}")


if __name__ == "__main__":
    run_settlement()
