[![Python 3.11](https://img.shields.io/badge/python-3.11-20232a?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Exchange CI](https://img.shields.io/github/actions/workflow/status/saksham10arora-dotcom/gitrade/market.yml?style=flat-square&label=exchange&color=238636)](https://github.com/saksham10arora-dotcom/gitrade/actions)
[![Settlement](https://img.shields.io/badge/settlement-sunday_00%3A00_UTC-e6842a?style=flat-square)](settle.py)
[![Bot League](https://img.shields.io/badge/bots-submit_a_PR-0d1117?style=flat-square&color=58a6ff)](CONTRIBUTING.md)

<!-- TIMESTAMP_START -->
_Last updated: 2026-07-24 20:41 UTC_
<!-- TIMESTAMP_END -->

---

## Market

<!-- STATS_START -->
| Ticker | Fair Value | Last Price | Signal |
|--------|-----------|------------|--------|
| $STAR | 0 | ? | ⚪ |
| $COMMIT | 0 | ? | ⚪ |
| $FORK | 0 | ? | ⚪ |
<!-- STATS_END -->

<!-- COUNTDOWN_START -->
**Settlement in: 1d 5h 5m**
<!-- COUNTDOWN_END -->

---

## Order Book

<!-- BOOK_START -->

**$STAR**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$COMMIT**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$FORK**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|
<!-- BOOK_END -->

---

## Trade

Open a GitHub Issue. The **title** is your order.

<table>
<tr>
<td><strong>Limit</strong></td>
<td><kbd>BUY $STAR 10 @ 45</kbd> &nbsp; <kbd>SELL $COMMIT 5 @ 12</kbd></td>
</tr>
<tr>
<td><strong>Market</strong></td>
<td><kbd>MARKET BUY $FORK 3</kbd></td>
</tr>
<tr>
<td><strong>Cancel</strong></td>
<td><kbd>CANCEL $STAR</kbd></td>
</tr>
</table>

CI picks it up within 15 min, closes the issue, updates the book. Every account starts at **$10,000**. Shorts work: sell without a position, profit if the price falls by Sunday.

---

## Leaderboards

### Human League

File issues. Any GitHub account can trade.

<!-- HUMAN_BOARD_START -->
| Rank | Name | P&L |
|------|------|-----|
| 🥇 | example_meanrev | +0 |
<!-- HUMAN_BOARD_END -->

### Bot League

Submit `bots/yourname.py` via PR. One function.

```python
NAME = "yourname"

def decide(market: dict) -> list:
    # market snapshot every 15 min:
    # tickers[t]: fair_value, best_bid, best_ask, last_price, price_history
    # my_cash, my_positions, settles_in_sec, week_number
    return [
        {"ticker": "STAR", "side": "BUY", "qty": 5, "price": 45.0},
    ]
```

Bots run sandboxed: **2s timeout**, **6 orders/tick max**. See [`bots/example_meanrev.py`](bots/example_meanrev.py) for a full template and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contract.

<!-- BOT_BOARD_START -->
| Rank | Name | P&L |
|------|------|-----|
| 🥇 | _mm | +0 |
| 🥈 | _momentum | +0 |
| 🥉 | _noise | +0 |
<!-- BOT_BOARD_END -->

---

## Settlement

Every **Sunday at 00:00 UTC**:

```
1. pull real GitHub stats (stars / commits-this-week / forks)
2. cash-settle all positions to those numbers
3. post champion Issue
4. reset all accounts to $10,000
```

The market price is where people think those numbers land. Settlement is where they actually land.

---

## Hall of Fame

<!-- HALLOFFAME_START -->
| Week | League | Champion | P&L |
|------|--------|----------|-----|
| 6 | bot | _mm | +0 |
| 6 | human | example_meanrev | +0 |
| 5 | bot | _mm | +0 |
| 5 | human | example_meanrev | +0 |
| 4 | bot | _mm | +0 |
| 4 | human | example_meanrev | +0 |
| 3 | bot | _mm | +0 |
| 3 | human | example_meanrev | +0 |
| 2 | bot | _mm | +-72 |
| 2 | human | example_meanrev | +350 |
<!-- HALLOFFAME_END -->

---

<details>
<summary><strong>Architecture</strong></summary>

<br>

```
gitrade/
├── engine.py           matching engine, P&L, settlement  (pure logic, no I/O)
├── market.py           15-min tick: parse issues -> run bots -> match -> render
├── settle.py           Sunday 00:00 UTC cron
├── render.py           state dict -> README marker sections
├── charts.py           neon SVG price + leaderboard charts
├── github_stats.py     live GitHub API (never raises, returns fallback)
│
├── bots/
│   ├── loader.py           discover + sandbox all bots (SIGALRM 2s)
│   ├── _mm.py              house market maker  (+/- 4% spread, SIZE=8)
│   ├── _noise.py           noise trader        (random, fair-value biased)
│   ├── _momentum.py        trend follower      (LOOKBACK=4)
│   └── example_meanrev.py  contributor baseline -- copy this
│
├── tools/
│   └── simulate.py         local tester: python3 tools/simulate.py 50
│
└── .github/workflows/
    ├── market.yml          cron */15 * * * *
    └── settle.yml          cron 0 0 * * 0
```

**State shape** (`state.json`):
```json
{
  "week_number": 1,
  "fair_value":  { "STAR": 0, "COMMIT": 0, "FORK": 0 },
  "books":       { "STAR": { "bids": [], "asks": [] }, ... },
  "accounts":    { "username": { "cash": 10000, "positions": {...} } },
  "price_history": { "STAR": [44, 45, 46], ... },
  "hall_of_fame": []
}
```

**Tick flow**:
```
fetch_real_stats()  ->  parse GitHub Issues  ->  run_all_bots()
       |                        |                       |
       v                        v                       v
  update fair_value       place_order()           place_order()
                                   \               /
                                    -> match fills
                                    -> save_state()
                                    -> update_readme()
                                    -> render charts
```

</details>

---

<sub>Built by <a href="https://github.com/saksham10arora-dotcom">@saksham10arora-dotcom</a></sub>
