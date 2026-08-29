"""
twap.py -- hourly TWAP sampler and settlement computation.

Called every hour by GitHub Actions. Appends one stats snapshot to
state["twap_samples"]. settle.py averages the last TWAP_WINDOW_HOURS
samples to produce the settlement price, eliminating single-snapshot manipulation.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path

from github_stats import fetch_real_stats

TWAP_WINDOW_HOURS = 24   # how many hours of samples to keep
STATE_FILE = Path("state.json")
REPO_NAME  = os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")


def record_sample(state: dict, stats: dict) -> None:
    """Append stats snapshot; trim samples older than TWAP_WINDOW_HOURS."""
    cutoff = time.time() - TWAP_WINDOW_HOURS * 3600
    samples = state.setdefault("twap_samples", [])
    samples.append({"ts": time.time(), "stats": stats})
    # Trim anything older than the window
    state["twap_samples"] = [s for s in samples if s["ts"] >= cutoff]


def compute_twap_settlement(state: dict, fallback: dict | None = None) -> dict:
    """
    Average all stats in twap_samples to produce settlement prices.
    Falls back to `fallback` dict if no samples exist.
    """
    from github_stats import _FALLBACK
    fb = _FALLBACK.copy() if fallback is None else fallback
    samples = state.get("twap_samples", [])
    if not samples:
        return fb

    from engine import TICKERS  # canonical list — don't derive from first sample
    averages = {}
    for t in TICKERS:
        vals = [s["stats"].get(t, 0) for s in samples]
        averages[t] = round(sum(vals) / len(vals), 4)
    return averages


def run_twap_sample():
    """Entry point: read state, fetch stats, append sample, save."""
    if not STATE_FILE.exists():
        print("No state.json found. Skipping TWAP sample.")
        return

    state = json.loads(STATE_FILE.read_text())
    prior = state.get("prior_week_snapshot")
    stats, new_snapshot = fetch_real_stats(prior_snapshot=prior, repo_name=REPO_NAME,
                                            fallback=state.get("fair_value"),
                                            star_cache=state)   # incremental fraud filter caches across ticks

    record_sample(state, stats)
    state["fair_value"] = stats   # keep fair_value current for mid-week marks

    if new_snapshot is not None:
        state["current_raw_snapshot"] = new_snapshot

    STATE_FILE.write_text(json.dumps(state, indent=2))
    print(f"TWAP sample recorded. Samples in window: {len(state['twap_samples'])}. Stats: {stats}")


if __name__ == "__main__":
    run_twap_sample()
