[![Python 3.11](https://img.shields.io/badge/python-3.11-20232a?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Exchange CI](https://img.shields.io/github/actions/workflow/status/saksham10arora-dotcom/gitrade/market.yml?style=flat-square&label=exchange&color=238636)](https://github.com/saksham10arora-dotcom/gitrade/actions)
[![Settlement](https://img.shields.io/badge/settlement-sunday_00%3A00_UTC-e6842a?style=flat-square)](settle.py)
[![Bot League](https://img.shields.io/badge/bots-submit_a_PR-0d1117?style=flat-square&color=58a6ff)](CONTRIBUTING.md)

<!-- TIMESTAMP_START -->
_Last updated: 2026-09-01 21:24 UTC_
<!-- TIMESTAMP_END -->

---

## Tickers

| Ticker | You're betting on | Trade |
|--------|-------------------|-------|
| $DSTAR | gitrade repo: clean new stars this week | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20DSTAR%201%20%40%205) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20DSTAR%201%20%40%205) |
| $DFORK | gitrade repo: new forks this week | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20DFORK%201%20%40%202) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20DFORK%201%20%40%202) |
| $VSCODE | microsoft/vscode: new stars this week | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20VSCODE%201%20%40%20200) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20VSCODE%201%20%40%20200) |
| $REACT | facebook/react: new stars this week | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20REACT%201%20%40%20150) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20REACT%201%20%40%20150) |
| $VSCREACT | vscode stars MINUS react stars | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20VSCREACT%201%20%40%2050) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20VSCREACT%201%20%40%2050) |
| $OAVSAN | OpenAI SDK stars MINUS Anthropic SDK stars | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20OAVSAN%201%20%40%2010) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20OAVSAN%201%20%40%2010) |
| $RUSTGO | Rust stars MINUS Go stars | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20RUSTGO%201%20%40%2050) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20RUSTGO%201%20%40%2050) |
| $BUNVNODE | Bun stars MINUS Node stars | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20BUNVNODE%201%20%40%2050) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20BUNVNODE%201%20%40%2050) |
| $NEXTREMIX | Next.js stars MINUS React Router stars | [BUY](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=BUY%20NEXTREMIX%201%20%40%2050) · [SELL](https://github.com/saksham10arora-dotcom/gitrade/issues/new?title=SELL%20NEXTREMIX%201%20%40%2050) |

Click a link, edit the qty/price in the issue title, hit submit. Your order fills on the next tick (15 min).
Spread tickers can go NEGATIVE: quoting `@ -20` is valid.

**How settlement works:** every ticker settles to the average of 24 hourly readings
taken over the final 24h of the week (TWAP). Each reading is the week-to-date delta
at that hour, so a last-minute star bomb moves settlement by at most 1/24th per hour.
The number on Sunday morning is the trailing average, NOT the final delta. That is the contract.

## Market

<!-- STATS_START -->
| Ticker | Fair Value | Last Price | Vol | Signal |
|--------|-----------|------------|-----|--------|
| $DSTAR | 0 | ? | 0 | ⚪ |
| $DFORK | 0 | ? | 0 | ⚪ |
| $VSCODE | 618 | 407.39 | 18 | 🟢 |
| $REACT | 614 | 381.65 | 39 | 🟢 |
| $VSCREACT | 4 | ? | 0 | ⚪ |
| $OAVSAN | 28 | ? | 0 | ⚪ |
| $RUSTGO | 73 | ? | 0 | ⚪ |
| $BUNVNODE | -536 | ? | 0 | ⚪ |
| $NEXTREMIX | 77 | ? | 0 | ⚪ |
<!-- STATS_END -->

<!-- COUNTDOWN_START -->
**Settlement in: 0d 0h 0m**
<!-- COUNTDOWN_END -->

---

## Order Book

<!-- BOOK_START -->

**$DSTAR**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$DFORK**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$VSCODE**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|
| ASK | 404.9 | 8 | _mm |
| ASK | 399.21 | 8 | _mm |
| ASK | 384.07 | 2 | _mm |
| BID | 593.28 | 8 | _mm |
| BID | 590.73 | 5 | _mm |
| BID | 582.72 | 6 | _mm |

**$REACT**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|
| ASK | 387.88 | 8 | _mm |
| ASK | 381.65 | 3 | example_meanrev |
| ASK | 381.65 | 6 | _mm |
| BID | 593.7 | 8 | _mm |
| BID | 589.44 | 8 | _mm |
| BID | 584.64 | 8 | _mm |

**$VSCREACT**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$OAVSAN**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$RUSTGO**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$BUNVNODE**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|

**$NEXTREMIX**
| Side | Price | Qty | Owner |
|------|-------|-----|-------|
<!-- BOOK_END -->

---

## Trade

Open a GitHub Issue. The **title** is your order.

<table>
<tr>
<td><strong>Limit</strong></td>
<td><kbd>BUY $DSTAR 10 @ 5</kbd> &nbsp; <kbd>SELL $VSCREACT 5 @ -20</kbd></td>
</tr>
<tr>
<td><strong>Market</strong></td>
<td><kbd>MARKET BUY $VSCODE 3</kbd></td>
</tr>
<tr>
<td><strong>Cancel</strong></td>
<td><kbd>CANCEL $DSTAR</kbd></td>
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
| 🥇 | example_meanrev | -480 |
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
        {"ticker": "DSTAR", "side": "BUY", "qty": 5, "price": 5.0},
    ]
```

Bots run sandboxed: **2s timeout**, **6 orders/tick max**. See [`bots/example_meanrev.py`](bots/example_meanrev.py) for a full template and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contract.

<!-- BOT_BOARD_START -->
| Rank | Name | P&L |
|------|------|-----|
| 🥇 | _mm | +1069 |
| 🥈 | _momentum | +0 |
| 🥉 | _noise | -590 |
<!-- BOT_BOARD_END -->

---

## Settlement

Every **Sunday at 00:01 UTC**:

```
1. compute each ticker's settlement = TWAP (average of 24 hourly readings
   over the final 24h of the week), not a single closing snapshot
2. cash-settle all positions to those numbers (signed: spreads settle +/-)
3. update persistent ELO for accounts that traded this week
4. post champion Issue
```

Balances PERSIST across weeks. There is no weekly reset. Your cash carries forward,
your ELO carries forward, and the weekly leaderboard ranks P&L since Monday.
House bots get topped up to a liquidity floor; humans carry their wins and losses.

The market price is where people think those numbers land. Settlement is where they actually land.

---

## Hall of Fame

<!-- HALLOFFAME_START -->
_No champions yet. First settlement is Sunday._
<!-- HALLOFFAME_END -->

## ELO Ladder

<!-- ELO_START -->
_No ELO data yet. First settlement unlocks the ladder._
<!-- ELO_END -->

## TWAP Settlement Progress

<!-- TWAP_START -->
**TWAP samples:** `█████░░░░░░░░░░░░░░░` 6/24h. Settlement price will average these readings
<!-- TWAP_END -->

---

<details>
<summary><strong>Architecture</strong></summary>

<br>

```
gitrade/
├── engine.py           matching engine, P&L, settlement  (pure logic, no I/O)
├── market.py           15-min tick: parse issues -> run bots -> match -> render
├── settle.py           Sunday 00:01 UTC cron
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
  "fair_value":  { "DSTAR": 0, "DFORK": 0, "VSCODE": 0, ... },
  "books":       { "DSTAR": { "bids": [], "asks": [] }, ... },
  "accounts":    { "username": { "cash": 10000, "positions": {...} } },
  "elo":          { "username": 1000, ... },
  "twap_samples": [],
  "price_history": { "DSTAR": [4, 5, 6], ... },
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
