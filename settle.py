"""
settle.py -- Sunday 00:01 UTC settlement job.

Reads TWAP samples from state.json, computes averaged settlement prices,
cash-settles all positions, updates ELO, posts champion issue.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

from github import Github, Auth

from engine import settle_week
from twap import compute_twap_settlement

STATE_FILE = Path("state.json")
REPO_NAME  = os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")
TOKEN      = os.environ.get("GITHUB_TOKEN", "")


def run_settlement():
    if not STATE_FILE.exists():
        print("No state.json found. Skipping settlement.")
        return

    state = json.loads(STATE_FILE.read_text())

    # Settlement price = TWAP average over last 24h samples.
    # Fallback: last known fair_value (single snapshot) if samples missing.
    settlement_prices = compute_twap_settlement(state, fallback=state.get("fair_value"))
    n_samples = len(state.get("twap_samples", []))
    print(f"Settling with {n_samples} TWAP samples. Prices: {settlement_prices}")

    summary = settle_week(state, settlement_prices)

    # Post champion issue
    if TOKEN:
        g = Github(auth=Auth.Token(TOKEN))
        repo = g.get_repo(REPO_NAME)

        lines = [
            f"## Week {state.get('week_number', '?') - 1} Settlement\n",
            f"Settlement method: TWAP ({n_samples} samples)\n",
            f"Settlement prices: {settlement_prices}\n",
            "\n### Results\n",
            "| Trader | P&L | ELO |",
            "|--------|-----|-----|",
        ]
        for name, data in sorted(summary.items(), key=lambda x: -x[1]["pnl"]):
            sign = "+" if data["pnl"] >= 0 else ""
            elo = state.get("elo", {}).get(name, 1000)
            lines.append(f"| {name} | {sign}{data['pnl']:.0f} | {elo:.0f} |")

        # Filter by settled week — hall[-2:] grabs a stale entry when one league had no traders
        settled_week = state.get("week_number", 1) - 1
        champs = [e for e in state.get("hall_of_fame", []) if e["week"] == settled_week]
        if champs:
            champions = [f"{e['name']} ({e['league']}, +{e['pnl']:.0f}, ELO {e.get('elo', 1000):.0f})" for e in champs]
            lines.append(f"\nChampions: {', '.join(champions)}")

        repo.create_issue(
            title=f"Settlement: Week {state.get('week_number', 1) - 1}",
            body="\n".join(lines),
        )

    STATE_FILE.write_text(json.dumps(state, indent=2))
    print(f"Settlement complete.")


if __name__ == "__main__":
    run_settlement()
