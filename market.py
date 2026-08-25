"""
market.py -- per-tick orchestrator.

Every 15 min via GitHub Actions:
  1. Fetch real GitHub stats (fair value)
  2. Parse open GitHub Issues as human orders
  3. Run all bots
  4. Match all orders
  5. Render README + charts + commit
"""

from __future__ import annotations
import json
import os
import re
import sys
import time
from pathlib import Path

from github import Github, Auth

from engine import place_order, cancel_orders, TICKERS, get_account
from github_stats import fetch_real_stats
from bots.loader import run_all_bots
from render import update_readme
from charts import price_chart, leaderboard_chart

STATE_FILE = Path("state.json")
REPO_NAME  = os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")
TOKEN      = os.environ.get("GITHUB_TOKEN", "")

# Build ticker alternation from the canonical TICKERS list (derived, not hardcoded).
# Price group allows a minus sign: spread tickers settle negative routinely.
_T = "|".join(TICKERS)
LIMIT_RE  = re.compile(rf"^(BUY|SELL)\s+\$?({_T})\s+(\d+)\s+@\s+(-?\d+(?:\.\d+)?)$", re.IGNORECASE)
MARKET_RE = re.compile(rf"^MARKET\s+(BUY|SELL)\s+\$?({_T})\s+(\d+)$", re.IGNORECASE)
CANCEL_RE = re.compile(rf"^CANCEL\s+\$?({_T})$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "week_number": 1,
        "week_start_ts": time.time(),
        "fair_value": {t: 0 for t in TICKERS},
        "books": {},
        "accounts": {},
        "last_price": {},
        "price_history": {},
        "hall_of_fame": [],
        "elo": {},
        "trader_cache": {},
        "twap_samples": [],
        "prior_week_snapshot": {
            "gitrade_stars": 0, "gitrade_forks": 0,
            "vscode_stars": 0, "react_stars": 0,
            "openai_sdk_stars": 0, "anthropic_sdk_stars": 0,
            "rust_stars": 0, "go_stars": 0,
            "bun_stars": 0, "node_stars": 0,
            "nextjs_stars": 0, "remix_stars": 0,
        },
        "current_raw_snapshot": {},
        "tick": 0,
    }


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def write_meta(state: dict):
    """Write state_meta.json for badge/dashboard use."""
    from engine import compute_pnl, split_leagues, mark_price
    humans, bots = split_leagues(state)
    meta = {
        "week": state.get("week_number", 1),
        "tick": state.get("tick", 0),
        "fair_value": state.get("fair_value", {}),
        "last_price": state.get("last_price", {}),
        "top_human": max(humans, key=lambda n: compute_pnl(state, n), default=None),
        "top_bot": max(bots, key=lambda n: compute_pnl(state, n), default=None),
    }
    Path("state_meta.json").write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# Issue parsing
# ---------------------------------------------------------------------------

def parse_order(title: str, owner: str, ts: float) -> dict | None:
    title = title.strip()

    m = LIMIT_RE.match(title)
    if m:
        side, ticker, qty, price = m.groups()
        return {
            "ticker": ticker.upper(),
            "side": side.upper(),
            "qty": int(qty),
            "price": float(price),
            "owner": owner,
            "ts": ts,
        }

    m = MARKET_RE.match(title)
    if m:
        side, ticker, qty = m.groups()
        return {
            "ticker": ticker.upper(),
            "side": side.upper(),
            "qty": int(qty),
            "price": None,
            "owner": owner,
            "ts": ts,
        }

    return None


def parse_cancel(title: str) -> str | None:
    m = CANCEL_RE.match(title.strip())
    if m:
        return m.group(1).upper()
    return None


# ---------------------------------------------------------------------------
# Main tick
# ---------------------------------------------------------------------------

def run_tick():
    state = load_state()
    tick = state.get("tick", 0) + 1
    state["tick"] = tick

    # 1. Update fair value from live GitHub stats
    fv = fetch_real_stats(REPO_NAME, fallback=state.get("fair_value", {}))
    state["fair_value"] = fv

    # 2. Parse GitHub Issues (human orders)
    if TOKEN:
        g = Github(auth=Auth.Token(TOKEN))
        repo = g.get_repo(REPO_NAME)
        for issue in repo.get_issues(state="open", labels=[]):
            owner = issue.user.login
            title = issue.title.strip()
            ts    = issue.created_at.timestamp()

            cancel_ticker = parse_cancel(title)
            if cancel_ticker:
                n = cancel_orders(state, owner, cancel_ticker)
                issue.edit(state="closed")
                continue

            order = parse_order(title, owner, ts)
            if order:
                place_order(state, order)
                issue.edit(state="closed")

    # 3. Run bots
    week_start = state.get("week_start_ts", time.time())
    settle_ts  = week_start + 7 * 86400
    settles_in = max(0, settle_ts - time.time())

    bot_orders = run_all_bots(state, tick, settles_in)
    for order in bot_orders:
        place_order(state, order)

    # 4. Persist + render
    save_state(state)
    write_meta(state)
    update_readme(state)
    price_chart(state)
    leaderboard_chart(state)

    print(f"Tick {tick} complete. FV={fv} Bots placed {len(bot_orders)} orders.")


if __name__ == "__main__":
    run_tick()
