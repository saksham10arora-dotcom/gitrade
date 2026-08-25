"""
_mm.py -- house market maker.
Quotes both sides around the EXTRAPOLATED weekly delta +/- SPREAD_FRAC.
Prefix _ marks it as a house bot (excluded from human leaderboard).
"""

NAME = "_mm"
SPREAD_FRAC = 0.04
SIZE = 8
TRADED = ["DSTAR", "DFORK", "VSCODE", "REACT"]  # liquid tickers; skip spreads for now

WEEK_SECONDS = 7 * 86400


def _extrapolated_fv(snap: dict, ticker: str) -> float:
    """Project the week-to-date delta to a full-week estimate.

    fair_value at 20% through the week is ~20% of the final settlement,
    so divide by elapsed fraction. Floor at 10% to avoid Monday-morning
    divide-by-near-zero blowups."""
    fv = snap["tickers"][ticker]["fair_value"] or 0
    elapsed = max(0.10, 1 - snap["settles_in_sec"] / WEEK_SECONDS)
    return fv / elapsed


def decide(market: dict) -> list:
    orders = []
    for ticker in TRADED:
        info = market["tickers"].get(ticker)
        if info is None:
            continue
        anchor = _extrapolated_fv(market, ticker) or info["last_price"]
        if anchor is None or anchor <= 0:
            continue
        bid = round(anchor * (1 - SPREAD_FRAC), 2)
        ask = round(anchor * (1 + SPREAD_FRAC), 2)
        orders.append({"ticker": ticker, "side": "BUY",  "qty": SIZE, "price": bid})
        orders.append({"ticker": ticker, "side": "SELL", "qty": SIZE, "price": ask})
    return orders
