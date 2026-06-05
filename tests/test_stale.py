"""Tests for the stale module."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from codex_maintainer.stale import (
    _add_label,
    _close_issue,
    _filter_stale,
    _list_open_issues,
    _post_comment,
)


def _make_issue(number: int, days_ago: int, labels: list[str] | None = None) -> dict:
    updated = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return {
        "number": number,
        "title": f"Issue #{number}",
        "updatedAt": updated,
        "labels": [{"name": lb} for lb in (labels or [])],
        "author": {"login": "user"},
        "url": f"https://github.com/owner/repo/issues/{number}",
    }


def test_filter_stale_returns_old_issues():
    issues = [_make_issue(1, days_ago=100), _make_issue(2, days_ago=10)]
    stale = _filter_stale(issues, days=90)
    assert len(stale) == 1
    assert stale[0]["number"] == 1


def test_filter_stale_returns_empty_when_none_old():
    issues = [_make_issue(1, days_ago=5), _make_issue(2, days_ago=20)]
    stale = _filter_stale(issues, days=90)
    assert stale == []


def test_filter_stale_skips_invalid_date():
    issues = [{"number": 99, "title": "Bad", "updatedAt": "not-a-date", "labels": []}]
    stale = _filter_stale(issues, days=1)
    assert stale == []


def test_list_open_issues_parses_json():
    fake = [_make_issue(1, days_ago=100)]
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(fake), returncode=0)
        result = _list_open_issues(None)
    assert result[0]["number"] == 1
    cmd = mock_run.call_args[0][0]
    assert "gh" in cmd
    assert "--state" in cmd
    assert "open" in cmd


def test_list_open_issues_passes_repo():
    fake: list[dict] = []
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(fake), returncode=0)
        _list_open_issues("owner/repo")
    cmd = mock_run.call_args[0][0]
    assert "--repo" in cmd
    assert "owner/repo" in cmd


def test_add_label_calls_gh():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        _add_label(42, "stale", None)
    cmd = mock_run.call_args[0][0]
    assert "gh" in cmd
    assert "stale" in cmd
    assert "42" in cmd


def test_post_comment_calls_gh():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        _post_comment(7, "hello", "owner/repo")
    cmd = mock_run.call_args[0][0]
    assert "comment" in cmd
    assert "hello" in cmd
    assert "--repo" in cmd


def test_close_issue_calls_gh():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        _close_issue(3, None)
    cmd = mock_run.call_args[0][0]
    assert "close" in cmd
    assert "3" in cmd
