"""
loader.py -- discover, sandbox, and run all bots each tick.
"""

from __future__ import annotations
import importlib
import importlib.util
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

BOTS_DIR = Path(__file__).parent
MAX_ORDERS_PER_BOT = 6
TIMEOUT_SEC = 2
VALID_SIDES = {"BUY", "SELL"}


def discover() -> list:
    """Return list of loaded bot modules from bots/."""
    bots = []
    for path in sorted(BOTS_DIR.glob("*.py")):
        if path.stem.startswith("__") or path.stem == "loader":
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if hasattr(mod, "decide") and hasattr(mod, "NAME"):
                bots.append(mod)
        except Exception:
            pass
    return bots


def _snapshot(state: dict, owner: str) -> dict:
    """Build the market snapshot passed to decide()."""
    from engine import compute_mid, best_bid, best_ask, TICKERS, STARTING_CASH, get_account

    tickers = {}
    for t in TICKERS:
        tickers[t] = {
            "fair_value": state.get("fair_value", {}).get(t),
            "best_bid": best_bid(state, t),
            "best_ask": best_ask(state, t),
            "last_price": state.get("last_price", {}).get(t),
            "price_history": list(state.get("price_history", {}).get(t, [])),
        }

    acct = get_account(state, owner)
    week_start = state.get("week_start_ts", time.time())
    settle_ts = week_start + 7 * 86400
    settles_in_sec = max(0, settle_ts - time.time())

    return {
        "tickers": tickers,
        "my_cash": acct["cash"],
        "my_positions": dict(acct["positions"]),
        "settles_in_sec": settles_in_sec,
        "week_number": state.get("week_number", 1),
    }


def _run_one(mod, snapshot: dict) -> list:
    """Run decide() with SIGALRM timeout. Returns raw output or []."""
    result = []

    def _handler(signum, frame):
        raise TimeoutError

    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(TIMEOUT_SEC)
    try:
        result = mod.decide(snapshot)
    except Exception:
        result = []
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)

    return result if isinstance(result, list) else []


def _clean_orders(raw: list, owner: str, ts: float) -> list:
    """Validate and tag orders from a bot."""
    from engine import TICKERS
    clean = []
    for o in raw[:MAX_ORDERS_PER_BOT]:
        try:
            ticker = str(o.get("ticker", "")).upper()
            side = str(o.get("side", "")).upper()
            qty = int(o.get("qty", 0))
            price = float(o.get("price", 0))
            if ticker not in TICKERS:
                continue
            if side not in VALID_SIDES:
                continue
            if qty <= 0 or price <= 0:
                continue
            clean.append({
                "ticker": ticker,
                "side": side,
                "qty": qty,
                "price": round(price, 2),
                "owner": owner,
                "ts": ts,
            })
        except Exception:
            continue
    return clean


def run_all_bots(state: dict, tick: int, settles_in_sec: float) -> list[dict]:
    """Discover all bots, run each, return flat list of validated orders."""
    all_orders = []
    ts = time.time()
    for mod in discover():
        owner = mod.NAME
        snap = _snapshot(state, owner)
        raw = _run_one(mod, snap)
        orders = _clean_orders(raw, owner, ts)
        all_orders.extend(orders)
    return all_orders
