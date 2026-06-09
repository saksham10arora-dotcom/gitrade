# Contributing to gitrade

## Beat my market maker

There are 3 house bots running: `_mm` (market maker), `_noise`, `_momentum`.

Your goal: write a bot that outperforms all of them by Sunday settlement.

---

## Bot contract

Create `bots/yourname.py`. No leading underscore (that prefix is reserved for house bots).

```python
NAME = "yourname"   # must match filename, no spaces

def decide(market: dict) -> list:
    ...
    return orders   # list of dicts, max 6
```

### The `market` snapshot

```python
{
  "tickers": {
    "STAR": {
      "fair_value": float | None,     # current GitHub star count
      "best_bid":   float | None,
      "best_ask":   float | None,
      "last_price": float | None,
      "price_history": [float, ...]   # last 50 filled prices
    },
    "COMMIT": { ... },
    "FORK":   { ... }
  },
  "my_cash":      float,              # current cash balance
  "my_positions": {                   # signed: + long, - short
    "STAR": int, "COMMIT": int, "FORK": int
  },
  "settles_in_sec": float,            # seconds until Sunday settlement
  "week_number":    int
}
```

### Order format

```python
{"ticker": "STAR", "side": "BUY", "qty": 5, "price": 45.0}
# side: "BUY" or "SELL"
# qty:  positive int
# price: positive float (limit only, no market orders for bots)
```

### Rules

- Max 6 orders returned per tick
- 2-second execution timeout (SIGALRM)
- No network calls, no file I/O, no imports outside stdlib + numpy
- Bot is reviewed before merging
- Your bot runs every 15 min all week
- Settlement: cash-settles to real GitHub numbers Sunday midnight UTC

---

## Submitting

1. Fork the repo
2. Add `bots/yourname.py`
3. Test locally: `python3 tools/simulate.py 20`
4. Open a PR

That is it. Once merged, your bot competes in the bot league.

---

## Local testing

```bash
pip install PyGithub matplotlib numpy
python3 tools/simulate.py        # 50 ticks, default
python3 tools/simulate.py 100    # 100 ticks
```

Simulate runs all bots, prints leaderboard, no GitHub token needed.
