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
