import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine import TICKERS, get_account, place_order


def test_tickers_v4():
    assert set(TICKERS) == {
        "DSTAR", "DFORK",
        "VSCODE", "REACT",
        "VSCREACT", "OAVSAN", "RUSTGO", "BUNVNODE", "NEXTREMIX",
    }


def test_account_has_v4_positions():
    state = {}
    acct = get_account(state, "alice")
    assert set(acct["positions"].keys()) == set(TICKERS)


def test_place_order_dstar():
    state = {}
    get_account(state, "alice")
    get_account(state, "bob")
    order_sell = {"ticker": "DSTAR", "side": "SELL", "qty": 5, "price": 10.0, "owner": "alice", "ts": 0.0}
    order_buy  = {"ticker": "DSTAR", "side": "BUY",  "qty": 5, "price": 10.0, "owner": "bob",   "ts": 1.0}
    place_order(state, order_sell)
    fills = place_order(state, order_buy)
    assert len(fills) == 1
    assert fills[0]["qty"] == 5
    assert fills[0]["price"] == 10.0


def test_negative_price_seller_margin_check():
    # Spread tickers settle negative; a SELL at a negative price makes the SELLER pay.
    # The seller must not be pushed below zero cash.
    state = {}
    seller = get_account(state, "seller")
    buyer = get_account(state, "buyer")
    seller["cash"] = 100.0   # only enough to cover 5 @ -20 (=100)
    # buyer rests a bid at -20; seller hits it selling 50 -> would cost 50*20=1000 > 100
    place_order(state, {"ticker": "VSCREACT", "side": "BUY", "qty": 50, "price": -20.0, "owner": "buyer", "ts": 0.0})
    fills = place_order(state, {"ticker": "VSCREACT", "side": "SELL", "qty": 50, "price": -20.0, "owner": "seller", "ts": 1.0})
    # Seller can only afford floor(100/20) = 5 units
    filled = sum(f["qty"] for f in fills)
    assert filled == 5
    assert state["accounts"]["seller"]["cash"] >= 0


# ---------------------------------------------------------------------------
# Task 4: persistent ELO + no cash reset
# ---------------------------------------------------------------------------
from engine import settle_week, compute_elo_update, STARTING_CASH


def test_elo_update_winner_gains():
    rankings = ["alice", "bob", "carol"]
    elo_before = {"alice": 1000, "bob": 1000, "carol": 1000}
    elo_after = compute_elo_update(elo_before, rankings)
    assert elo_after["alice"] > 1000
    assert elo_after["carol"] < 1000
    assert elo_after["bob"] > elo_after["carol"]


def test_elo_tie_scores_half():
    rankings = ["a", "b"]
    pnls = {"a": 100.0, "b": 100.0}
    elo_after = compute_elo_update({"a": 1000, "b": 1000}, rankings, pnls)
    assert elo_after["a"] == 1000
    assert elo_after["b"] == 1000


def test_settle_does_not_reset_cash():
    state = {
        "accounts": {
            "alice": {"cash": 10500.0, "positions": {"DSTAR": 10, "DFORK": 0, "VSCODE": 0, "REACT": 0, "SPREAD": 0}, "league": "human"},
            "bob":   {"cash":  9500.0, "positions": {"DSTAR": 0, "DFORK": 0, "VSCODE": 0, "REACT": 0, "SPREAD": 0}, "league": "human"},
        },
        "books": {}, "elo": {"alice": 1020, "bob": 980}, "twap_samples": [],
        "hall_of_fame": [], "week_number": 2, "prior_week_snapshot": {}, "current_raw_snapshot": {},
    }
    real_stats = {"DSTAR": 5, "DFORK": 1, "VSCODE": 200, "REACT": 180, "SPREAD": 20}
    settle_week(state, real_stats)
    alice_cash = state["accounts"]["alice"]["cash"]
    assert alice_cash != STARTING_CASH
    assert alice_cash == 10500.0 + 10 * 5


def test_settle_updates_elo():
    state = {
        "accounts": {
            "winner": {"cash": 11000.0, "positions": {t: 0 for t in ["DSTAR","DFORK","VSCODE","REACT","SPREAD"]}, "league": "human"},
            "loser":  {"cash":  9000.0, "positions": {t: 0 for t in ["DSTAR","DFORK","VSCODE","REACT","SPREAD"]}, "league": "human"},
        },
        "books": {}, "elo": {}, "twap_samples": [], "hall_of_fame": [],
        "week_number": 1, "prior_week_snapshot": {}, "current_raw_snapshot": {},
        "active_this_week": ["winner", "loser"],
    }
    real_stats = {"DSTAR": 3, "DFORK": 1, "VSCODE": 100, "REACT": 80, "SPREAD": 20}
    settle_week(state, real_stats)
    assert state["elo"]["winner"] > 1000
    assert state["elo"]["loser"]  < 1000


def test_settle_ranks_by_weekly_pnl_not_lifetime():
    state = {
        "accounts": {
            "rich_idle": {"cash": 15000.0, "cash_at_week_start": 15000.0,
                          "positions": {t: 0 for t in ["DSTAR","DFORK","VSCODE","REACT","SPREAD"]}, "league": "human"},
            "grinder":   {"cash": 10500.0, "cash_at_week_start": 10000.0,
                          "positions": {t: 0 for t in ["DSTAR","DFORK","VSCODE","REACT","SPREAD"]}, "league": "human"},
        },
        "books": {}, "elo": {}, "twap_samples": [], "hall_of_fame": [],
        "week_number": 5, "prior_week_snapshot": {}, "current_raw_snapshot": {},
        "active_this_week": ["grinder"],
    }
    real_stats = {"DSTAR": 3, "DFORK": 1, "VSCODE": 100, "REACT": 80, "SPREAD": 20}
    summary = settle_week(state, real_stats)
    assert summary["rich_idle"]["pnl"] == 0
    assert summary["grinder"]["pnl"] == 500
    assert "rich_idle" not in state["elo"]


def test_bot_refill_floor():
    state = {
        "accounts": {
            "_mm": {"cash": 200.0, "cash_at_week_start": 200.0,
                    "positions": {t: 0 for t in ["DSTAR","DFORK","VSCODE","REACT","SPREAD"]}, "league": "human"},
        },
        "books": {}, "elo": {}, "twap_samples": [], "hall_of_fame": [],
        "week_number": 3, "prior_week_snapshot": {}, "current_raw_snapshot": {},
    }
    real_stats = {"DSTAR": 0, "DFORK": 0, "VSCODE": 0, "REACT": 0, "SPREAD": 0}
    settle_week(state, real_stats)
    assert state["accounts"]["_mm"]["cash"] == 1000.0
    assert state["accounts"]["_mm"]["cash_at_week_start"] == 1000.0


def test_settle_clears_positions_after_settlement():
    state = {
        "accounts": {
            "alice": {"cash": 10000.0, "positions": {"DSTAR": 5, "DFORK": 0, "VSCODE": 0, "REACT": 0, "SPREAD": 0}, "league": "human"},
        },
        "books": {}, "elo": {}, "twap_samples": [], "hall_of_fame": [],
        "week_number": 1, "prior_week_snapshot": {}, "current_raw_snapshot": {},
    }
    real_stats = {"DSTAR": 4, "DFORK": 0, "VSCODE": 100, "REACT": 90, "SPREAD": 10}
    settle_week(state, real_stats)
    assert state["accounts"]["alice"]["positions"]["DSTAR"] == 0


# ---------------------------------------------------------------------------
# Guard coverage (from final review — Important 5)
# ---------------------------------------------------------------------------
from engine import MAX_POSITION, compute_weekly_pnl


def test_bankrupt_account_cannot_order():
    state = {}
    acct = get_account(state, "broke")
    acct["cash"] = 0.0
    get_account(state, "mm")
    place_order(state, {"ticker": "DSTAR", "side": "SELL", "qty": 5, "price": 10.0, "owner": "mm", "ts": 0.0})
    fills = place_order(state, {"ticker": "DSTAR", "side": "BUY", "qty": 5, "price": 10.0, "owner": "broke", "ts": 1.0})
    assert fills == []   # rejected outright, no fills


def test_self_trade_prevented():
    state = {}
    get_account(state, "alice")
    place_order(state, {"ticker": "DSTAR", "side": "SELL", "qty": 5, "price": 10.0, "owner": "alice", "ts": 0.0})
    fills = place_order(state, {"ticker": "DSTAR", "side": "BUY", "qty": 5, "price": 10.0, "owner": "alice", "ts": 1.0})
    assert fills == []   # cannot match own resting order
    assert state["accounts"]["alice"]["positions"]["DSTAR"] == 0


def test_max_position_caps_aggressor():
    state = {}
    get_account(state, "whale")
    get_account(state, "seller")
    # seller offers 100 DSTAR; whale tries to buy all 100 but is capped at MAX_POSITION
    place_order(state, {"ticker": "DSTAR", "side": "SELL", "qty": 100, "price": 1.0, "owner": "seller", "ts": 0.0})
    fills = place_order(state, {"ticker": "DSTAR", "side": "BUY", "qty": 100, "price": 1.0, "owner": "whale", "ts": 1.0})
    assert sum(f["qty"] for f in fills) == MAX_POSITION
    assert state["accounts"]["whale"]["positions"]["DSTAR"] == MAX_POSITION


def test_max_position_caps_passive():
    state = {}
    get_account(state, "resting")
    get_account(state, "hitter")
    # resting party posts a 100-lot bid; passive limit caps its accumulation at MAX_POSITION
    place_order(state, {"ticker": "DSTAR", "side": "BUY", "qty": 100, "price": 1.0, "owner": "resting", "ts": 0.0})
    place_order(state, {"ticker": "DSTAR", "side": "SELL", "qty": 100, "price": 1.0, "owner": "hitter", "ts": 1.0})
    assert abs(state["accounts"]["resting"]["positions"]["DSTAR"]) == MAX_POSITION


def test_buyer_margin_truncates_positive_price():
    state = {}
    buyer = get_account(state, "buyer")
    get_account(state, "seller")
    buyer["cash"] = 30.0   # can afford only 3 @ 10
    place_order(state, {"ticker": "DSTAR", "side": "SELL", "qty": 10, "price": 10.0, "owner": "seller", "ts": 0.0})
    fills = place_order(state, {"ticker": "DSTAR", "side": "BUY", "qty": 10, "price": 10.0, "owner": "buyer", "ts": 1.0})
    assert sum(f["qty"] for f in fills) == 3
    assert state["accounts"]["buyer"]["cash"] >= 0


def test_settle_negative_spread_price():
    # A short position on a spread ticker settling NEGATIVE pays the short holder.
    state = {
        "accounts": {
            "shorty": {"cash": 10000.0, "cash_at_week_start": 10000.0,
                       "positions": {t: 0 for t in TICKERS}, "league": "human"},
        },
        "books": {}, "elo": {}, "twap_samples": [], "hall_of_fame": [],
        "week_number": 2, "prior_week_snapshot": {}, "current_raw_snapshot": {},
    }
    state["accounts"]["shorty"]["positions"]["NEXTREMIX"] = -10   # short 10
    real_stats = {t: 0 for t in TICKERS}
    real_stats["NEXTREMIX"] = -20   # settles negative
    settle_week(state, real_stats)
    # short 10 * settlement -20 => cash += (-10)*(-20) = +200
    assert state["accounts"]["shorty"]["cash"] == 10200.0
    assert state["accounts"]["shorty"]["positions"]["NEXTREMIX"] == 0


def test_compute_weekly_pnl_uses_week_start():
    state = {"accounts": {"g": {"cash": 10500.0, "cash_at_week_start": 10000.0,
                                "positions": {t: 0 for t in TICKERS}, "league": "human"}}}
    assert compute_weekly_pnl(state, "g") == 500.0
