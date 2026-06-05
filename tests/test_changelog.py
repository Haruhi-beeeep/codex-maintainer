"""Tests for the changelog module."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from codex_maintainer.changelog import _get_latest_tag, _get_git_log


def test_get_latest_tag_returns_tag_string():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="v1.2.3\n", returncode=0)
        result = _get_latest_tag()
    assert result == "v1.2.3"


def test_get_latest_tag_returns_none_when_no_tags():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = _get_latest_tag()
    assert result is None


def test_get_git_log_with_range():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="feat: add login\n---\n", returncode=0)
        result = _get_git_log("v1.0.0", "HEAD")
    assert "feat: add login" in result
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert "v1.0.0..HEAD" in cmd


def test_get_git_log_without_since():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="fix: crash on startup\n---\n", returncode=0)
        result = _get_git_log(None, "HEAD")
    assert "fix: crash on startup" in result
    cmd = mock_run.call_args[0][0]
    assert ".." not in str(cmd)
