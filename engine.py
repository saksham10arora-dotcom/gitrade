"""
engine.py -- pure trading logic, no I/O.

Tickers: STAR, COMMIT, FORK (GitHub stats as underlyings).
Positions are signed (positive = long, negative = short).
All settlement is cash-only against real GitHub numbers.
"""

from __future__ import annotations
import time
from typing import Optional

TICKERS = [
    "DSTAR", "DFORK",                          # Tier 1: personal repo deltas
    "VSCODE", "REACT",                          # Tier 2: solo external deltas
    "VSCREACT", "OAVSAN", "RUSTGO",            # Tier 2: spread markets
    "BUNVNODE", "NEXTREMIX",
]
STARTING_CASH = 10_000
MAX_POSITION = 50   # per account per ticker
BOT_PREFIX = "_"   # house bots; excluded from human leaderboard


# ---------------------------------------------------------------------------
# Order book helpers
# ---------------------------------------------------------------------------

def _book(state: dict, ticker: str) -> dict:
    return state.setdefault("books", {}).setdefault(ticker, {"bids": [], "asks": []})


def best_bid(state: dict, ticker: str) -> Optional[float]:
    bids = _book(state, ticker)["bids"]
    return max((o["price"] for o in bids), default=None)


def best_ask(state: dict, ticker: str) -> Optional[float]:
    asks = _book(state, ticker)["asks"]
    return min((o["price"] for o in asks), default=None)


def compute_mid(state: dict, ticker: str) -> Optional[float]:
    bid = best_bid(state, ticker)
    ask = best_ask(state, ticker)
    if bid is not None and ask is not None:
        return (bid + ask) / 2
    if bid is not None:
        return bid
    if ask is not None:
        return ask
    return None


def mark_price(state: dict, ticker: str) -> Optional[float]:
    """Mid-week mark: prefer market mid, fall back to fair_value."""
    mid = compute_mid(state, ticker)
    if mid is not None:
        return mid
    return state.get("fair_value", {}).get(ticker)


# ---------------------------------------------------------------------------
# Account helpers
# ---------------------------------------------------------------------------

def get_account(state: dict, name: str) -> dict:
    return state.setdefault("accounts", {}).setdefault(name, {
        "cash": STARTING_CASH,
        "cash_at_week_start": STARTING_CASH,   # baseline for weekly P&L / ELO ranking
        "positions": {t: 0 for t in TICKERS},
        "league": "human",
    })


def compute_equity(state: dict, name: str) -> float:
    acct = get_account(state, name)
    eq = acct["cash"]
    for ticker in TICKERS:
        qty = acct["positions"].get(ticker, 0)
        if qty == 0:
            continue
        mp = mark_price(state, ticker)
        if mp is not None:
            eq += qty * mp
    return eq


def compute_pnl(state: dict, name: str) -> float:
    return compute_equity(state, name) - STARTING_CASH


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------

def place_order(state: dict, order: dict) -> list[dict]:
    """
    Place one order, run matching, return list of fill events.

    order schema:
      ticker: str
      side: "BUY" | "SELL"
      qty: int (positive)
      price: float | None   (None = market order)
      owner: str
      ts: float (unix)
    """
    # Bankrupt accounts can't open new orders. One-time restart grant: v4.1.
    if get_account(state, order["owner"])["cash"] <= 0:
        return []

    ticker = order["ticker"]
    book = _book(state, ticker)
    fills = []

    signed_qty = order["qty"] if order["side"] == "BUY" else -order["qty"]
    remaining = abs(signed_qty)
    aggressor_sign = 1 if order["side"] == "BUY" else -1

    # Determine passive side
    if order["side"] == "BUY":
        passive_side = "asks"
        price_ok = lambda passive_p: order["price"] is None or passive_p <= order["price"]
        passive_sort = lambda o: (o["price"], o["ts"])
    else:
        passive_side = "bids"
        price_ok = lambda passive_p: order["price"] is None or passive_p >= order["price"]
        passive_sort = lambda o: (-o["price"], o["ts"])

    passive_book = sorted(book[passive_side], key=passive_sort)
    new_passive = []

    for passive in passive_book:
        if passive["owner"] == order["owner"]:   # no self-match — prevents wash trading
            new_passive.append(passive)
            continue
        if remaining == 0:
            new_passive.append(passive)
            continue
        if not price_ok(passive["price"]):
            new_passive.append(passive)
            continue

        fill_qty = min(remaining, passive["qty"])
        fill_price = passive["price"]

        # Position limit on the AGGRESSOR — caps max loss on spread tickers.
        aggressor = get_account(state, order["owner"])
        pos_after = aggressor["positions"].get(ticker, 0) + aggressor_sign * fill_qty
        if abs(pos_after) > MAX_POSITION:
            fill_qty = max(0, MAX_POSITION - abs(aggressor["positions"].get(ticker, 0)))

        # Enforce on the PASSIVE party too — without this, resting orders
        # let an account accumulate unlimited position (limit bypass).
        passive_acct = get_account(state, passive["owner"])
        passive_after = passive_acct["positions"].get(ticker, 0) - aggressor_sign * fill_qty
        if abs(passive_after) > MAX_POSITION:
            allowed = MAX_POSITION - abs(passive_acct["positions"].get(ticker, 0))
            fill_qty = max(0, min(fill_qty, allowed))

        if fill_qty == 0:
            new_passive.append(passive)
            continue

        # Positive-price margin check — buyer pays cash, truncate to what they can afford.
        buyer_name = order["owner"] if order["side"] == "BUY" else passive["owner"]
        buyer_acct = get_account(state, buyer_name)
        if fill_price > 0 and buyer_acct["cash"] < fill_qty * fill_price:
            fill_qty = max(0, int(buyer_acct["cash"] // fill_price))
        if fill_qty == 0:
            new_passive.append(passive)
            continue

        # Negative-price margin check — spread tickers settle negative, so the
        # SELLER pays cash. Symmetric to the buyer check above.
        if fill_price < 0:
            seller_name = passive["owner"] if order["side"] == "BUY" else order["owner"]
            seller_acct = get_account(state, seller_name)
            cost = fill_qty * abs(fill_price)
            if seller_acct["cash"] < cost:
                fill_qty = max(0, int(seller_acct["cash"] // abs(fill_price)))
            if fill_qty == 0:
                new_passive.append(passive)
                continue

        # Update aggressor account
        aggressor = get_account(state, order["owner"])
        aggressor["cash"] -= aggressor_sign * fill_qty * fill_price
        aggressor["positions"][ticker] = aggressor["positions"].get(ticker, 0) + aggressor_sign * fill_qty

        # Update passive account
        passive_sign = -aggressor_sign
        passive_acct = get_account(state, passive["owner"])
        passive_acct["cash"] -= passive_sign * fill_qty * fill_price
        passive_acct["positions"][ticker] = passive_acct["positions"].get(ticker, 0) + passive_sign * fill_qty

        fills.append({
            "ticker": ticker,
            "price": fill_price,
            "qty": fill_qty,
            "buyer": order["owner"] if order["side"] == "BUY" else passive["owner"],
            "seller": passive["owner"] if order["side"] == "BUY" else order["owner"],
            "ts": order["ts"],
        })

        remaining -= fill_qty
        if passive["qty"] > fill_qty:
            leftover = dict(passive)
            leftover["qty"] = passive["qty"] - fill_qty
            new_passive.append(leftover)

    book[passive_side] = new_passive

    # Rest of order goes on the book
    if remaining > 0 and order["price"] is not None:
        resting = {
            "owner": order["owner"],
            "qty": remaining,
            "price": order["price"],
            "ts": order["ts"],
        }
        active_side = "bids" if order["side"] == "BUY" else "asks"
        book[active_side].append(resting)

    # Record last price
    if fills:
        state.setdefault("last_price", {})[ticker] = fills[-1]["price"]
        history = state.setdefault("price_history", {}).setdefault(ticker, [])
        history.extend(f["price"] for f in fills)
        if len(history) > 50:
            state["price_history"][ticker] = history[-50:]

    return fills


def cancel_orders(state: dict, owner: str, ticker: str) -> int:
    book = _book(state, ticker)
    before = sum(len(book[s]) for s in ("bids", "asks"))
    book["bids"] = [o for o in book["bids"] if o["owner"] != owner]
    book["asks"] = [o for o in book["asks"] if o["owner"] != owner]
    after = sum(len(book[s]) for s in ("bids", "asks"))
    return before - after


# ---------------------------------------------------------------------------
# League split
# ---------------------------------------------------------------------------

def split_leagues(state: dict) -> tuple[list[str], list[str]]:
    """Returns (human_names, bot_names)."""
    accounts = state.get("accounts", {})
    humans = [n for n in accounts if not n.startswith(BOT_PREFIX)]
    bots = [n for n in accounts if n.startswith(BOT_PREFIX)]
    return humans, bots


# ---------------------------------------------------------------------------
# Settlement
# ---------------------------------------------------------------------------

def settle_week(state: dict, real_stats: dict) -> dict:
    """
    Cash-settle all positions to real GitHub numbers.
    Returns a summary dict with P&L for every account.
    real_stats: {"STAR": int, "COMMIT": int, "FORK": int}
    """
    summary = {}
    for name, acct in state.get("accounts", {}).items():
        equity_before = compute_equity(state, name)
        cash = acct["cash"]

        for ticker, qty in acct["positions"].items():
            real = real_stats.get(ticker)
            if real is None or qty == 0:
                continue
            settlement_value = qty * real
            cash += settlement_value

        pnl = cash - STARTING_CASH
        summary[name] = {
            "final_cash": round(cash, 2),
            "pnl": round(pnl, 2),
            "equity_before_settle": round(equity_before, 2),
        }

    # Crown champions
    humans, bots = split_leagues(state)
    human_summary = {n: summary[n] for n in humans if n in summary}
    bot_summary = {n: summary[n] for n in bots if n in summary}

    best_human = max(human_summary, key=lambda n: human_summary[n]["pnl"], default=None)
    best_bot = max(bot_summary, key=lambda n: bot_summary[n]["pnl"], default=None)

    hall = state.setdefault("hall_of_fame", [])
    week = state.get("week_number", 1)
    if best_human:
        hall.append({"week": week, "league": "human", "name": best_human, "pnl": human_summary[best_human]["pnl"]})
    if best_bot:
        hall.append({"week": week, "league": "bot", "name": best_bot, "pnl": bot_summary[best_bot]["pnl"]})

    # Reset state for new week
    state["accounts"] = {}
    state["books"] = {}
    state["last_price"] = {}
    state["price_history"] = {}
    state["fair_value"] = real_stats.copy()
    state["week_number"] = week + 1
    state["week_start_ts"] = time.time()

    return summary
