"""Tests for the triage module."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from codex_maintainer.triage import TriageResult, _get_issue_data


def test_triage_result_model():
    data = {
        "type": "bug",
        "priority": "high",
        "labels": ["bug", "needs-investigation"],
        "summary": "App crashes on empty input.",
        "suggested_action": "Reproduce and add a null check.",
        "complexity": "small",
    }
    result = TriageResult.model_validate(data)
    assert result.type == "bug"
    assert result.priority == "high"
    assert len(result.labels) == 2


def test_get_issue_data_parses_json():
    fake_data = {
        "title": "App crashes",
        "body": "Steps to reproduce...",
        "author": {"login": "user123"},
        "createdAt": "2026-01-01T00:00:00Z",
    }
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(fake_data), returncode=0)
        result = _get_issue_data(42, None)
    assert result["title"] == "App crashes"
    assert result["author"]["login"] == "user123"


def test_get_issue_data_uses_repo_flag():
    fake_data = {"title": "T", "body": "", "author": {"login": "u"}, "createdAt": "2026-01-01"}
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=json.dumps(fake_data), returncode=0)
        _get_issue_data(1, "owner/repo")
    cmd = mock_run.call_args[0][0]
    assert "--repo" in cmd
    assert "owner/repo" in cmd
