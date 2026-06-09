# gitrade

> Buy `$STAR` if you think this repo blows up. Short `$COMMIT` if you think it dies. Sunday, GitHub tells us who was right.

A futures market that runs entirely inside this GitHub repo. No server. No database. GitHub Actions is the exchange. `state.json` is the order book.

<!-- TIMESTAMP_START -->
_Last updated: initializing..._
<!-- TIMESTAMP_END -->

---

## Live Market

<!-- STATS_START -->
| Ticker | Fair Value | Last Price | Signal |
|--------|-----------|------------|--------|
| $STAR | 0 | -- | ⚪ |
| $COMMIT | 0 | -- | ⚪ |
| $FORK | 0 | -- | ⚪ |
<!-- STATS_END -->

> 🟢 price below fair value (cheap)   🔴 price above fair value (expensive)

<!-- COUNTDOWN_START -->
**Settlement in: calculating...**
<!-- COUNTDOWN_END -->

---

## Order Book

<!-- BOOK_START -->
_No open orders._
<!-- BOOK_END -->

---

## How to Trade

**Place a limit order** -- open an Issue with this title:

```
BUY $STAR 10 @ 45
SELL $COMMIT 5 @ 12
```

**Market order:**
```
MARKET BUY $FORK 3
```

**Cancel your open orders on a ticker:**
```
CANCEL $STAR
```

CI processes your issue within 15 minutes, closes it, and updates the book.

Every account starts with **$10,000**. Positions settle Sunday midnight UTC.

---

## Two Leagues

### Human League

Anyone can trade. File issues. Watch the board.

<!-- HUMAN_BOARD_START -->
_No participants yet._
<!-- HUMAN_BOARD_END -->

### Bot League

Submit a `bots/yourname.py` via PR with one function:

```python
NAME = "yourname"

def decide(market: dict) -> list:
    # market has: tickers (fair_value, best_bid, best_ask, last_price, price_history)
    #             my_cash, my_positions, settles_in_sec
    return [
        {"ticker": "STAR", "side": "BUY", "qty": 5, "price": 45.0},
    ]
```

See `bots/example_meanrev.py` for a full template. See `CONTRIBUTING.md` for rules.

<!-- BOT_BOARD_START -->
_No bots yet._
<!-- BOT_BOARD_END -->

---

## Settlement

Every Sunday at 00:00 UTC:

1. Real GitHub stats are pulled (stars, commits this week, forks)
2. All positions cash-settle to those numbers
3. Champions are posted as an Issue
4. All accounts reset to $10,000

The market price is what people think those numbers will be. The settlement is what they actually are.

---

## Hall of Fame

<!-- HALLOFFAME_START -->
_No champions yet. First settlement is Sunday._
<!-- HALLOFFAME_END -->

---

## Architecture

```
engine.py          pure matching logic (no I/O)
market.py          15-min tick orchestrator
settle.py          Sunday settlement cron
render.py          state -> README sections
charts.py          neon SVG charts -> assets/
github_stats.py    live GitHub API fetcher
bots/
  loader.py        bot discovery + sandboxing (2s timeout)
  _mm.py           house market maker
  _noise.py        noise trader
  _momentum.py     trend follower
  example_meanrev.py  contributor baseline
.github/workflows/
  market.yml       runs market.py every 15 min
  settle.yml       runs settle.py every Sunday 00:00 UTC
```

**Want to contribute a bot?** Read `CONTRIBUTING.md`.

---

## FAQ

**Can I short?**
Yes. `SELL $STAR 10 @ 45` with no existing position opens a short. If stars end below 45 on Sunday, you profit.

**What if my order does not fill?**
It rests in the book until someone takes the other side, or until you cancel it.

**Who are the house bots?**
`_mm` (market maker), `_noise` (random trader), `_momentum` (trend follower). They keep liquidity alive. They compete in the bot league only.

**Is this real money?**
No. All accounts start at $10,000 of play money. Settlement is bragging rights.
