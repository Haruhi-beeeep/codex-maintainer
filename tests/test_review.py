"""Tests for the review module."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from codex_maintainer.review import _get_pr_diff, _get_pr_metadata


def test_get_pr_diff_calls_gh_cli():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="diff --git a/foo.py...", returncode=0)
        result = _get_pr_diff(7, None)
    assert "diff" in result
    cmd = mock_run.call_args[0][0]
    assert "gh" in cmd
    assert "7" in cmd


def test_get_pr_diff_passes_repo_flag():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        _get_pr_diff(7, "owner/repo")
    cmd = mock_run.call_args[0][0]
    assert "--repo" in cmd
    assert "owner/repo" in cmd


def test_get_pr_metadata_parses_json():
    fake = {
        "title": "Add feature X",
        "body": "This PR adds...",
        "headRefName": "feat/x",
        "baseRefName": "main",
        "author": {"login": "contributor"},
    }
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(fake), returncode=0)
        result = _get_pr_metadata(7, None)
    assert result["title"] == "Add feature X"
    assert result["author"]["login"] == "contributor"
