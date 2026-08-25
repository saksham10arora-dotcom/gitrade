import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from twap import record_sample, compute_twap_settlement, TWAP_WINDOW_HOURS


def _make_samples(n: int, base: dict) -> list:
    now = time.time()
    return [{"ts": now - (n - i) * 3600, "stats": base} for i in range(n)]


def test_record_sample_appends():
    state = {"twap_samples": []}
    stats = {"DSTAR": 3, "DFORK": 1, "VSCODE": 200, "REACT": 150, "SPREAD": 50}
    record_sample(state, stats)
    assert len(state["twap_samples"]) == 1
    assert state["twap_samples"][0]["stats"] == stats


def test_record_sample_trims_old():
    state = {"twap_samples": []}
    old_stats = {"DSTAR": 1, "DFORK": 0, "VSCODE": 100, "REACT": 90, "SPREAD": 10}
    now = time.time()
    for i in range(30):
        state["twap_samples"].append({"ts": now - (TWAP_WINDOW_HOURS + 2) * 3600 - i, "stats": old_stats})
    new_stats = {"DSTAR": 5, "DFORK": 2, "VSCODE": 210, "REACT": 155, "SPREAD": 55}
    record_sample(state, new_stats)
    assert len(state["twap_samples"]) == 1
    assert state["twap_samples"][0]["stats"] == new_stats


def test_compute_twap_settlement_averages():
    base_a = {"DSTAR": 4, "DFORK": 2, "VSCODE": 200, "REACT": 150, "SPREAD": 50}
    base_b = {"DSTAR": 6, "DFORK": 4, "VSCODE": 220, "REACT": 170, "SPREAD": 50}
    samples = _make_samples(12, base_a) + _make_samples(12, base_b)
    state = {"twap_samples": samples}
    result = compute_twap_settlement(state)
    assert result["DSTAR"]  == 5     # mean(4, 6)
    assert result["DFORK"]  == 3     # mean(2, 4)
    assert result["VSCODE"] == 210   # mean(200, 220)


def test_compute_twap_fallback_when_no_samples():
    state = {"twap_samples": []}
    fallback = {"DSTAR": 1, "DFORK": 0, "VSCODE": 100, "REACT": 80, "SPREAD": 20}
    result = compute_twap_settlement(state, fallback=fallback)
    assert result == fallback


def test_compute_twap_needs_min_samples():
    state = {"twap_samples": [{"ts": time.time(), "stats": {"DSTAR": 3, "DFORK": 1, "VSCODE": 100, "REACT": 90, "SPREAD": 10}}]}
    result = compute_twap_settlement(state)
    assert result["DSTAR"] == 3
