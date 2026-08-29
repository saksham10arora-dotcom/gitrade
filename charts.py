"""
charts.py -- neon SVG charts written into assets/.
Dark-mode native. Glow via path_effects.
"""

from __future__ import annotations
from pathlib import Path
import io

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

_NEON = {
    "DSTAR":     "#00e5ff",
    "DFORK":     "#ff4081",
    "VSCODE":    "#2196f3",
    "REACT":     "#61dafb",
    "VSCREACT":  "#7c4dff",
    "OAVSAN":    "#d97757",
    "RUSTGO":    "#ff7043",
    "BUNVNODE":  "#f9f1e1",
    "NEXTREMIX": "#76ff03",
    "pos":       "#76ff03",   # leaderboard gain bars (was COMMIT)
    "neg":       "#ff4081",   # leaderboard loss bars (was FORK)
    "fair":   "#ffffff",
    "bg":     "#0d1117",
    "grid":   "#21262d",
    "text":   "#8b949e",
}


def _glow(color: str, lw: int = 3, alpha: float = 0.3):
    try:
        from matplotlib.patheffects import withStroke
        return [withStroke(linewidth=lw, foreground=color, alpha=alpha)]
    except Exception:
        return []


def price_chart(state: dict):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
    except ImportError:
        return

    from engine import TICKERS

    fig, axes = plt.subplots(len(TICKERS), 1, figsize=(10, 3 * len(TICKERS)),
                             facecolor=_NEON["bg"])
    if len(TICKERS) == 1:
        axes = [axes]

    for ax, ticker in zip(axes, TICKERS):
        ax.set_facecolor(_NEON["bg"])
        for spine in ax.spines.values():
            spine.set_color(_NEON["grid"])

        hist = state.get("price_history", {}).get(ticker, [])
        color = _NEON.get(ticker, "#ffffff")

        if hist:
            xs = list(range(len(hist)))
            ax.plot(xs, hist, color=color, linewidth=1.5,
                    path_effects=_glow(color))

        fv = state.get("fair_value", {}).get(ticker)
        if fv is not None:
            ax.axhline(fv, color=_NEON["fair"], linewidth=1,
                       linestyle="--", alpha=0.5, label="fair value")

        ax.set_title(f"${ticker}", color=color, fontsize=11, pad=6)
        ax.tick_params(colors=_NEON["text"])
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
        ax.grid(color=_NEON["grid"], linewidth=0.5)

    fig.tight_layout(pad=2)
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", facecolor=_NEON["bg"], bbox_inches="tight")
    plt.close(fig)
    (ASSETS / "price_chart.svg").write_bytes(buf.getvalue())


def leaderboard_chart(state: dict):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    from engine import compute_weekly_pnl

    accounts = state.get("accounts", {})
    if not accounts:
        return

    names = list(accounts.keys())
    pnls = [compute_weekly_pnl(state, n) for n in names]
    colors = [_NEON["pos"] if p >= 0 else _NEON["neg"] for p in pnls]

    fig, ax = plt.subplots(figsize=(8, max(3, len(names) * 0.5)),
                           facecolor=_NEON["bg"])
    ax.set_facecolor(_NEON["bg"])
    for spine in ax.spines.values():
        spine.set_color(_NEON["grid"])

    y = list(range(len(names)))
    ax.barh(y, pnls, color=colors, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(names, color=_NEON["text"], fontsize=9)
    ax.axvline(0, color=_NEON["text"], linewidth=0.8)
    ax.set_xlabel("P&L ($)", color=_NEON["text"])
    ax.tick_params(colors=_NEON["text"])
    ax.grid(axis="x", color=_NEON["grid"], linewidth=0.5)
    ax.set_title("Leaderboard P&L", color=_NEON["fair"], fontsize=11)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", facecolor=_NEON["bg"], bbox_inches="tight")
    plt.close(fig)
    (ASSETS / "leaderboard.svg").write_bytes(buf.getvalue())
