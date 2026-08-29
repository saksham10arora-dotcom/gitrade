"""
example_meanrev.py -- mean-reversion baseline for contributors.
Copy this file, rename it (no leading _), change NAME, tweak the logic.
Submit via PR.
"""

NAME = "example_meanrev"
EDGE = 0.06


def decide(market: dict) -> list:
    """
    market snapshot:
    {
      "tickers": {
        "DSTAR": {
          "fair_value": float | None,
          "best_bid": float | None,
          "best_ask": float | None,
          "last_price": float | None,
          "price_history": [float, ...]  # last 50 ticks
        },
        ...
      },
      "my_cash": float,
      "my_positions": {"DSTAR": int, "DFORK": int, ...},  # all 9 v4 tickers
      "settles_in_sec": float,
      "week_number": int
    }

    Return a list of up to 6 orders:
    [{"ticker": "DSTAR", "side": "BUY", "qty": 5, "price": 5.0}, ...]
    """
    orders = []
    for ticker, info in market["tickers"].items():
        fv = info.get("fair_value")
        last = info.get("last_price")
        anchor = fv or last
        if anchor is None or anchor <= 0:
            continue

        bid = info.get("best_bid")
        ask = info.get("best_ask")

        # If market is above fair value by EDGE, sell; if below, buy
        if fv is not None:
            if ask is not None and ask > fv * (1 + EDGE):
                orders.append({"ticker": ticker, "side": "SELL", "qty": 3, "price": ask})
            elif bid is not None and bid < fv * (1 - EDGE):
                orders.append({"ticker": ticker, "side": "BUY", "qty": 3, "price": bid})

    return orders
