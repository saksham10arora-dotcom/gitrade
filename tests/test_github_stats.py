import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from github_stats import _compute_deltas, _is_likely_bot_account, _FALLBACK


def test_compute_deltas_normal():
    current = {
        "gitrade_stars": 105, "gitrade_forks": 12,
        "vscode_stars": 168000, "react_stars": 228000,
        "openai_sdk_stars": 5000, "anthropic_sdk_stars": 3000,
        "rust_stars": 100000, "go_stars": 120000,
        "bun_stars": 75000, "node_stars": 108000,
        "nextjs_stars": 130000, "remix_stars": 30000,
    }
    prior = {
        "gitrade_stars": 100, "gitrade_forks": 10,
        "vscode_stars": 167800, "react_stars": 227700,
        "openai_sdk_stars": 4900, "anthropic_sdk_stars": 2950,
        "rust_stars": 99800, "go_stars": 119900,
        "bun_stars": 74900, "node_stars": 107990,
        "nextjs_stars": 129900, "remix_stars": 29980,
    }
    result = _compute_deltas(current, prior)
    assert result["DSTAR"]    == 5
    assert result["DFORK"]    == 2
    assert result["VSCODE"]   == 200
    assert result["REACT"]    == 300
    assert result["VSCREACT"] == 200 - 300          # -100
    assert result["OAVSAN"]   == 100 - 50           # 50
    assert result["RUSTGO"]   == 200 - 100          # 100
    assert result["BUNVNODE"] == 100 - 10           # 90
    assert result["NEXTREMIX"]== 100 - 20           # 80


def test_bot_account_detection():
    assert _is_likely_bot_account(account_age_days=5, num_repos=0, followers=0) is True
    assert _is_likely_bot_account(account_age_days=120, num_repos=8, followers=3) is False
    assert _is_likely_bot_account(account_age_days=30, num_repos=3, followers=1) is False


def test_fallback_keys():
    assert set(_FALLBACK.keys()) == {
        "DSTAR", "DFORK", "VSCODE", "REACT",
        "VSCREACT", "OAVSAN", "RUSTGO", "BUNVNODE", "NEXTREMIX",
    }
