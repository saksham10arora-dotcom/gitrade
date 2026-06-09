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

        # commits this week
        since = datetime.now(timezone.utc) - timedelta(days=7)
        commit_count = r.get_commits(since=since).totalCount

        return {
            "STAR": r.stargazers_count,
            "COMMIT": commit_count,
            "FORK": r.forks_count,
        }
    except Exception:
        return fb
