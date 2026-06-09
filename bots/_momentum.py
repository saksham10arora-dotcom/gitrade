"""
_momentum.py -- momentum follower.
Buys if recent prices are rising, sells if falling.
"""

NAME = "_momentum"
LOOKBACK = 4
SIZE = 5
EDGE = 0.02


def decide(market: dict) -> list:
    orders = []
    for ticker, info in market["tickers"].items():
        hist = info.get("price_history", [])
        anchor = info["fair_value"] or info["last_price"]
        if anchor is None or anchor <= 0:
            continue
        if len(hist) < LOOKBACK:
            continue
        recent = hist[-LOOKBACK:]
        trend = recent[-1] - recent[0]
        if trend > 0:
            # price rising -- buy above mid
            price = round(anchor * (1 + EDGE), 2)
            orders.append({"ticker": ticker, "side": "BUY", "qty": SIZE, "price": price})
        elif trend < 0:
            # price falling -- sell below mid
            price = round(anchor * (1 - EDGE), 2)
            orders.append({"ticker": ticker, "side": "SELL", "qty": SIZE, "price": price})
    return orders
