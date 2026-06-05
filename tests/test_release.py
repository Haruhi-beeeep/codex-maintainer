"""Tests for the release module."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from codex_maintainer.release import _get_commit_log, _get_contributors, _get_previous_tag


def test_get_commit_log_with_since():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Haruhi Abe: feat: add login\n---\n", returncode=0)
        result = _get_commit_log("v1.0.0")
    assert "feat: add login" in result
    cmd = mock_run.call_args[0][0]
    assert "v1.0.0..HEAD" in cmd


def test_get_commit_log_without_since():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Haruhi Abe: fix: crash\n---\n", returncode=0)
        result = _get_commit_log(None)
    assert "fix: crash" in result
    cmd = mock_run.call_args[0][0]
    assert ".." not in str(cmd)


def test_get_contributors_deduplicates():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Alice\nBob\nAlice\n", returncode=0)
        result = _get_contributors("v1.0.0")
    assert result == ["Alice", "Bob"]


def test_get_contributors_without_since():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Alice\n", returncode=0)
        result = _get_contributors(None)
    assert result == ["Alice"]
    cmd = mock_run.call_args[0][0]
    assert ".." not in str(cmd)


def test_get_previous_tag_returns_tag():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="v0.9.0\n", returncode=0)
        result = _get_previous_tag()
    assert result == "v0.9.0"


def test_get_previous_tag_returns_none_on_failure():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = _get_previous_tag()
    assert result is None
