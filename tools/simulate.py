"""
simulate.py -- local bot tester. No GitHub token needed.

Usage:
  python3 tools/simulate.py [N_TICKS]
"""

import sys
import time
from pathlib import Path

# ensure project root is on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from engine import place_order, compute_pnl, split_leagues, TICKERS, STARTING_CASH
from bots.loader import run_all_bots

N_TICKS = int(sys.argv[1]) if len(sys.argv) > 1 else 50


def fresh_state(stars=10, commits=5, forks=2) -> dict:
    return {
        "week_number": 1,
        "week_start_ts": time.time(),
        "fair_value": {"STAR": stars, "COMMIT": commits, "FORK": forks},
        "books": {},
        "accounts": {},
        "last_price": {},
        "price_history": {},
        "hall_of_fame": [],
        "tick": 0,
    }


def run_sim():
    state = fresh_state()
    print(f"Running {N_TICKS} ticks. Fair value: {state['fair_value']}\n")

    for tick in range(1, N_TICKS + 1):
        state["tick"] = tick
        orders = run_all_bots(state, tick, settles_in_sec=3 * 86400)
        for o in orders:
            place_order(state, o)

        if tick % 10 == 0:
            print(f"--- Tick {tick} ---")
            for t in TICKERS:
                book = state.get("books", {}).get(t, {})
                bids = book.get("bids", [])
                asks = book.get("asks", [])
                best_b = max((o["price"] for o in bids), default=None)
                best_a = min((o["price"] for o in asks), default=None)
                lp = state.get("last_price", {}).get(t, "none")
                print(f"  ${t}: bid={best_b} ask={best_a} last={lp}")
            print()

    print("=== Final Leaderboard ===")
    accounts = state.get("accounts", {})
    ranked = sorted(accounts.keys(), key=lambda n: compute_pnl(state, n), reverse=True)
    for name in ranked:
        pnl = compute_pnl(state, name)
        sign = "+" if pnl >= 0 else ""
        print(f"  {name}: {sign}{pnl:.0f}")


if __name__ == "__main__":
    run_sim()
