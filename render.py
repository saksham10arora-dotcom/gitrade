"""
render.py -- state dict -> README sections.
Uses marker-based surgery: <!-- X_START --> / <!-- X_END --> blocks.
"""

from __future__ import annotations
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from engine import compute_pnl, TICKERS, STARTING_CASH, split_leagues, mark_price

README = Path(__file__).parent / "README.md"


def _replace_section(text: str, tag: str, content: str) -> str:
    pattern = rf"(<!-- {tag}_START -->).*?(<!-- {tag}_END -->)"
    replacement = rf"\1\n{content}\n\2"
    return re.sub(pattern, replacement, text, flags=re.DOTALL)


def _countdown(state: dict) -> str:
    week_start = state.get("week_start_ts", time.time())
    settle_ts = week_start + 7 * 86400
    remaining = max(0, settle_ts - time.time())
    days = int(remaining // 86400)
    hours = int((remaining % 86400) // 3600)
    mins = int((remaining % 3600) // 60)
    return f"**Settlement in: {days}d {hours}h {mins}m**"


def _stats_table(state: dict) -> str:
    fv = state.get("fair_value", {})
    lp = state.get("last_price", {})
    vol = state.get("weekly_volume", {})
    lines = ["| Ticker | Fair Value | Last Price | Vol | Signal |",
             "|--------|-----------|------------|-----|--------|"]
    for t in TICKERS:
        f = fv.get(t, "?")
        l = lp.get(t, "?")
        v = vol.get(t, 0)
        if isinstance(f, (int, float)) and isinstance(l, (int, float)):
            dot = "🟢" if l < f else "🔴"
        else:
            dot = "⚪"
        lines.append(f"| ${t} | {f} | {l} | {v} | {dot} |")
    return "\n".join(lines)


def _book_table(state: dict) -> str:
    lines = []
    for t in TICKERS:
        book = state.get("books", {}).get(t, {"bids": [], "asks": []})
        bids = sorted(book["bids"], key=lambda o: -o["price"])[:3]
        asks = sorted(book["asks"], key=lambda o: o["price"])[:3]
        lines.append(f"\n**${t}**")
        lines.append("| Side | Price | Qty | Owner |")
        lines.append("|------|-------|-----|-------|")
        for o in asks[::-1]:
            lines.append(f"| ASK | {o['price']} | {o['qty']} | {o['owner']} |")
        for o in bids:
            lines.append(f"| BID | {o['price']} | {o['qty']} | {o['owner']} |")
    return "\n".join(lines)


def _leaderboard(state: dict, league: str) -> str:
    accounts = state.get("accounts", {})
    if league == "human":
        names = [n for n in accounts if not n.startswith("_")]
    else:
        names = [n for n in accounts if n.startswith("_")]

    if not names:
        return "_No participants yet._"

    ranked = sorted(names, key=lambda n: compute_pnl(state, n), reverse=True)
    lines = ["| Rank | Name | P&L |", "|------|------|-----|"]
    medals = ["🥇", "🥈", "🥉"]
    for i, name in enumerate(ranked[:10]):
        pnl = compute_pnl(state, name)
        sign = "+" if pnl >= 0 else ""
        medal = medals[i] if i < 3 else str(i + 1)
        lines.append(f"| {medal} | {name} | {sign}{pnl:.0f} |")
    return "\n".join(lines)


def _hall_of_fame(state: dict) -> str:
    hall = state.get("hall_of_fame", [])
    if not hall:
        return "_No champions yet. First settlement is Sunday._"
    lines = ["| Week | League | Champion | P&L |", "|------|--------|----------|-----|"]
    for entry in reversed(hall[-10:]):
        lines.append(f"| {entry['week']} | {entry['league']} | {entry['name']} | +{entry['pnl']:.0f} |")
    return "\n".join(lines)


def _timestamp() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"_Last updated: {now}_"


def _elo_ladder(state: dict) -> str:
    elo = state.get("elo", {})
    if not elo:
        return "_No ELO data yet. First settlement unlocks the ladder._"
    ranked = sorted(elo.items(), key=lambda x: -x[1])
    lines = ["| Rank | Trader | ELO |", "|------|--------|-----|"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, score) in enumerate(ranked[:10]):
        medal = medals[i] if i < 3 else str(i + 1)
        lines.append(f"| {medal} | {name} | {score:.0f} |")
    return "\n".join(lines)


def _twap_progress(state: dict) -> str:
    from twap import TWAP_WINDOW_HOURS
    samples = state.get("twap_samples", [])
    n = len(samples)
    target = TWAP_WINDOW_HOURS
    pct = min(100, int(n / target * 100))
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    return f"**TWAP samples:** `{bar}` {n}/{target}h. Settlement price will average these readings"


def update_readme(state: dict):
    text = README.read_text()
    text = _replace_section(text, "STATS", _stats_table(state))
    text = _replace_section(text, "COUNTDOWN", _countdown(state))
    text = _replace_section(text, "BOOK", _book_table(state))
    text = _replace_section(text, "HUMAN_BOARD", _leaderboard(state, "human"))
    text = _replace_section(text, "BOT_BOARD", _leaderboard(state, "bot"))
    text = _replace_section(text, "HALLOFFAME", _hall_of_fame(state))
    text = _replace_section(text, "ELO", _elo_ladder(state))
    text = _replace_section(text, "TWAP", _twap_progress(state))
    text = _replace_section(text, "TIMESTAMP", _timestamp())
    README.write_text(text)
