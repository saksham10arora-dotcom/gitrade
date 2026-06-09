<div align="left">

# gitrade

**A futures market inside a GitHub repo.**

Three tickers. Real underlying. Weekly settlement to actual GitHub stats.

[![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square)](https://python.org)
[![CI](https://img.shields.io/github/actions/workflow/status/saksham10arora-dotcom/gitrade/market.yml?style=flat-square&label=exchange)](https://github.com/saksham10arora-dotcom/gitrade/actions)
[![Settlement](https://img.shields.io/badge/settlement-sunday_00%3A00_UTC-zinc?style=flat-square)](https://github.com/saksham10arora-dotcom/gitrade/blob/main/settle.py)

</div>

---

<!-- TIMESTAMP_START -->
_Last updated: initializing..._
<!-- TIMESTAMP_END -->

---

## The Market

Three tickers, all derived from this repo's real GitHub stats:

| Ticker | Underlying | Fair Value |
|--------|-----------|------------|
| `$STAR` | stargazer count at settlement | current stars |
| `$COMMIT` | commits pushed this week | commits so far |
| `$FORK` | fork count at settlement | current forks |

Price floats freely all week. Sunday midnight UTC, real GitHub numbers are pulled. All positions cash-settle. Gap between price and fair value is the trade.

<!-- STATS_START -->
| Ticker | Fair Value | Last Price | Signal |
|--------|-----------|------------|--------|
| $STAR | 0 | -- | -- |
| $COMMIT | 0 | -- | -- |
| $FORK | 0 | -- | -- |
<!-- STATS_END -->

<!-- COUNTDOWN_START -->
**Settlement in: calculating...**
<!-- COUNTDOWN_END -->

---

## Order Book

<!-- BOOK_START -->
_No open orders._
<!-- BOOK_END -->

---

## Trading

Open a GitHub Issue. Title is the order.

**Limit order**
```
BUY $STAR 10 @ 45
SELL $COMMIT 5 @ 12
```

**Market order**
```
MARKET BUY $FORK 3
```

**Cancel resting orders**
```
CANCEL $STAR
```

CI processes each issue within 15 minutes, closes it, and updates the book. Every account starts with $10,000. Shorts work: sell something you do not own, profit if the price falls by Sunday.

---

## Two Leagues

### Human

File Issues. Any GitHub account can trade.

<!-- HUMAN_BOARD_START -->
_No participants yet._
<!-- HUMAN_BOARD_END -->

### Bot

Submit a PR with `bots/yourname.py`. One function. No leading underscore in the filename.

```python
NAME = "yourname"

def decide(market: dict) -> list:
    return [
        {"ticker": "STAR", "side": "BUY", "qty": 5, "price": 45.0},
    ]
```

`market` contains per-ticker `fair_value`, `best_bid`, `best_ask`, `last_price`, `price_history` (last 50 fills), plus `my_cash`, `my_positions`, `settles_in_sec`.

Bots run every 15 minutes. 2-second timeout. 6 orders per tick max. See `bots/example_meanrev.py` for a full template and `CONTRIBUTING.md` for the full contract.

<!-- BOT_BOARD_START -->
_No bots yet._
<!-- BOT_BOARD_END -->

---

## Settlement

Every Sunday at 00:00 UTC:

1. Real GitHub stats pulled via API
2. All positions cash-settle to those numbers
3. Champions posted as a GitHub Issue
4. All accounts reset to $10,000, new week begins

---

## Hall of Fame

<!-- HALLOFFAME_START -->
_No champions yet. First settlement is Sunday._
<!-- HALLOFFAME_END -->

---

## Files

```
engine.py           matching engine, P&L, settlement  (pure logic, no I/O)
market.py           15-min tick: parse issues, run bots, match, render
settle.py           Sunday 00:00 UTC settlement cron
render.py           state dict -> README marker sections
charts.py           neon SVG price + leaderboard charts
github_stats.py     live GitHub API fetcher (never raises)

bots/
  _mm.py            house market maker (+/- 4% spread)
  _noise.py         noise trader
  _momentum.py      trend follower (LOOKBACK=4)
  example_meanrev.py    contributor baseline -- copy this

tools/
  simulate.py       local tester: python3 tools/simulate.py 50

.github/workflows/
  market.yml        cron every 15 min
  settle.yml        cron Sunday 00:00 UTC
```

---

_Built by [@saksham10arora-dotcom](https://github.com/saksham10arora-dotcom)_
