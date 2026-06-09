"""github_stats.py -- fetch real GitHub stats for settlement."""

from __future__ import annotations
import os
from datetime import datetime, timezone, timedelta

_FALLBACK = {"STAR": 0, "COMMIT": 0, "FORK": 0}


def fetch_real_stats(repo=None, fallback: dict | None = None) -> dict:
    """
    Pull STAR, COMMIT (this week), FORK from GitHub API.
    Never raises. Returns fallback on any error.
    """
    fb = fallback or _FALLBACK.copy()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo_name = repo or os.environ.get("GITHUB_REPOSITORY", "saksham10arora-dotcom/gitrade")
    if not token:
        return fb

    try:
        from github import Github, Auth
        g = Github(auth=Auth.Token(token))
        r = g.get_repo(repo_name)

        # commits this week -- exclude the exchange's own automated commits
        # (market/settle ticks push with [skip ci] as market-bot, which would
        # otherwise inflate $COMMIT by ~672/week regardless of real dev work)
        since = datetime.now(timezone.utc) - timedelta(days=7)
        commit_count = 0
        for c in r.get_commits(since=since):
            msg = (c.commit.message or "")
            author = (c.commit.author.name or "") if c.commit.author else ""
            if "[skip ci]" in msg or author == "market-bot":
                continue
            commit_count += 1

        return {
            "STAR": r.stargazers_count,
            "COMMIT": commit_count,
            "FORK": r.forks_count,
        }
    except Exception:
        return fb
