"""
_noise.py -- noise trader.
Randomly buys or sells a subset of tickers, weakly biased toward fair_value.
"""

import random

NAME = "_noise"
EDGE = 0.06
TICKERS_TO_NOISE = ["DSTAR", "DFORK", "REACT"]


def decide(market: dict) -> list:
    orders = []
    for ticker in TICKERS_TO_NOISE:
        info = market["tickers"].get(ticker)
        if info is None:
            continue
        anchor = info["fair_value"] or info["last_price"]
        if anchor is None or anchor <= 0:
            continue
        price = round(anchor * (1 + random.uniform(-EDGE, EDGE)), 2)
        side = random.choice(["BUY", "SELL"])
        qty = random.randint(1, 5)
        orders.append({"ticker": ticker, "side": side, "qty": qty, "price": price})
    return orders
