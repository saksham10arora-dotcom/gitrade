"""github_stats.py -- fetch real GitHub stats for v4 settlement."""
from __future__ import annotations
import os
from datetime import datetime, timezone, timedelta

_FALLBACK: dict = {
    "DSTAR": 0, "DFORK": 0,
    "VSCODE": 0, "REACT": 0,
    "VSCREACT": 0, "OAVSAN": 0, "RUSTGO": 0, "BUNVNODE": 0, "NEXTREMIX": 0,
}

# External repos whose weekly star deltas are tracked (outside owner's control)
_EXTERNAL = {
    "vscode":        "microsoft/vscode",
    "react":         "facebook/react",
    "openai_sdk":    "openai/openai-python",
    "anthropic_sdk": "anthropics/anthropic-sdk-python",
    "rust":          "rust-lang/rust",
    "go":            "golang/go",
    "bun":           "oven-sh/bun",
    "node":          "nodejs/node",
    "nextjs":        "vercel/next.js",
    "remix":         "remix-run/react-router",
}

FRAUD_AGE_DAYS  = 30   # accounts newer than this are suspect
FRAUD_MIN_REPOS = 3    # must have at least this many repos
FRAUD_MIN_FOLLOWERS = 1  # must have at least 1 follower


def _is_likely_bot_account(account_age_days: int, num_repos: int, followers: int) -> bool:
    """Return True if account looks like a star-farm bot."""
    return account_age_days < FRAUD_AGE_DAYS and num_repos < FRAUD_MIN_REPOS and followers < FRAUD_MIN_FOLLOWERS


def _compute_deltas(current: dict, prior: dict) -> dict:
    """Compute v4 ticker values from current and prior raw snapshots."""
    def d(key): return current.get(key, 0) - prior.get(key, 0)

    vscode       = d("vscode_stars")
    react        = d("react_stars")
    openai_sdk   = d("openai_sdk_stars")
    anthropic_sdk= d("anthropic_sdk_stars")
    rust         = d("rust_stars")
    go           = d("go_stars")
    bun          = d("bun_stars")
    node         = d("node_stars")
    nextjs       = d("nextjs_stars")
    remix        = d("remix_stars")

    return {
        "DSTAR":    d("gitrade_stars"),
        "DFORK":    d("gitrade_forks"),
        "VSCODE":   vscode,
        "REACT":    react,
        "VSCREACT": vscode - react,
        "OAVSAN":   openai_sdk - anthropic_sdk,
        "RUSTGO":   rust - go,
        "BUNVNODE": bun - node,
        "NEXTREMIX":nextjs - remix,
    }


def fetch_raw_snapshot(repo_name: str = None, token: str = None,
                       star_cache: dict | None = None) -> dict | None:
    """
    Pull raw counts for gitrade repo + external repos.
    star_cache: pass state dict — incremental fraud filter only checks NEW stargazers,
                avoiding O(total_stars) API calls every hour (rate limit: 5000 req/hr).
    Returns None on any error (caller should use prior snapshot as fallback).
    """
    _token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    _repo  = repo_name or os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")
    if not _token:
        return None

    try:
        from github import Github, Auth
        g = Github(auth=Auth.Token(_token))

        r_gitrade = g.get_repo(_repo)

        # Incremental fraud filter — only fetch user details for logins not yet classified.
        # `known` maps login->is_clean bool; persisted in state["star_cache"] across ticks.
        # After week 1 (all existing stars classified), only NEW stargazers require API calls.
        now = datetime.now(timezone.utc)
        cache = star_cache or {}
        known: dict = cache.get("star_cache", {})

        # Classify only NEW stargazers (API-cheap), but count from the CURRENT
        # stargazer set so an unstar decrements the total. A cache-sum would be
        # monotonic and inflate DSTAR forever as people unstar.
        current_logins = []
        for sg in r_gitrade.get_stargazers_with_dates():
            login = sg.user.login
            current_logins.append(login)
            if login in known:
                continue  # already classified — no extra API call
            u = sg.user
            age_days = (now - u.created_at).days
            known[login] = not _is_likely_bot_account(age_days, u.public_repos, u.followers)

        clean_stars = sum(1 for login in current_logins if known.get(login))

        if star_cache is not None:
            star_cache["star_cache"] = known   # persist for next tick

        snapshot = {
            "gitrade_stars":       clean_stars,
            "gitrade_forks":       r_gitrade.forks_count,
            "vscode_stars":        g.get_repo(_EXTERNAL["vscode"]).stargazers_count,
            "react_stars":         g.get_repo(_EXTERNAL["react"]).stargazers_count,
            "openai_sdk_stars":    g.get_repo(_EXTERNAL["openai_sdk"]).stargazers_count,
            "anthropic_sdk_stars": g.get_repo(_EXTERNAL["anthropic_sdk"]).stargazers_count,
            "rust_stars":          g.get_repo(_EXTERNAL["rust"]).stargazers_count,
            "go_stars":            g.get_repo(_EXTERNAL["go"]).stargazers_count,
            "bun_stars":           g.get_repo(_EXTERNAL["bun"]).stargazers_count,
            "node_stars":          g.get_repo(_EXTERNAL["node"]).stargazers_count,
            "nextjs_stars":        g.get_repo(_EXTERNAL["nextjs"]).stargazers_count,
            "remix_stars":         g.get_repo(_EXTERNAL["remix"]).stargazers_count,
        }
        return snapshot
    except Exception:
        return None


def fetch_real_stats(prior_snapshot: dict | None = None,
                     repo_name: str = None,
                     fallback: dict | None = None,
                     star_cache: dict | None = None) -> tuple[dict, dict | None]:
    """
    Fetch current stats and compute v4 ticker deltas against prior_snapshot.
    Returns (stats_dict, new_raw_snapshot).
    Pass star_cache=state to enable incremental fraud filter caching.
    If fetch fails, returns (fallback, None).
    """
    fb = fallback or _FALLBACK.copy()
    current = fetch_raw_snapshot(repo_name, star_cache=star_cache)
    if current is None:
        return fb, None

    prior = prior_snapshot or {k: current[k] for k in current}  # zero-delta on week 1

    return _compute_deltas(current, prior), current
