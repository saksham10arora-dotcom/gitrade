"""
_momentum.py -- momentum follower on the star-delta ticker.
Buys if recent prices are rising, sells if falling.
"""

NAME = "_momentum"
TICKER = "DSTAR"   # momentum strategy on star delta
LOOKBACK = 4
SIZE = 5
EDGE = 0.02


def decide(market: dict) -> list:
    info = market["tickers"].get(TICKER)
    if info is None:
        return []
    hist = info.get("price_history", [])
    anchor = info["fair_value"] or info["last_price"]
    if anchor is None or anchor <= 0:
        return []
    if len(hist) < LOOKBACK:
        return []
    recent = hist[-LOOKBACK:]
    trend = recent[-1] - recent[0]
    if trend > 0:
        price = round(anchor * (1 + EDGE), 2)
        return [{"ticker": TICKER, "side": "BUY", "qty": SIZE, "price": price}]
    elif trend < 0:
        price = round(anchor * (1 - EDGE), 2)
        return [{"ticker": TICKER, "side": "SELL", "qty": SIZE, "price": price}]
    return []
