"""
_mm.py -- house market maker.
Quotes both sides around anchor price +/- SPREAD_FRAC.
Prefix _ marks it as a house bot (excluded from human leaderboard).
"""

NAME = "_mm"
SPREAD_FRAC = 0.04
SIZE = 8


def decide(market: dict) -> list:
    orders = []
    for ticker, info in market["tickers"].items():
        anchor = info["fair_value"] or info["last_price"]
        if anchor is None or anchor <= 0:
            continue
        bid = round(anchor * (1 - SPREAD_FRAC), 2)
        ask = round(anchor * (1 + SPREAD_FRAC), 2)
        orders.append({"ticker": ticker, "side": "BUY",  "qty": SIZE, "price": bid})
        orders.append({"ticker": ticker, "side": "SELL", "qty": SIZE, "price": ask})
    return orders
