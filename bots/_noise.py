"""
_noise.py -- noise trader.
Randomly buys or sells, weakly biased toward fair_value.
"""

import random

NAME = "_noise"
EDGE = 0.06


def decide(market: dict) -> list:
    orders = []
    for ticker, info in market["tickers"].items():
        anchor = info["fair_value"] or info["last_price"]
        if anchor is None or anchor <= 0:
            continue
        # random price within +/- EDGE of anchor
        price = round(anchor * (1 + random.uniform(-EDGE, EDGE)), 2)
        side = random.choice(["BUY", "SELL"])
        qty = random.randint(1, 5)
        orders.append({"ticker": ticker, "side": side, "qty": qty, "price": price})
    return orders
