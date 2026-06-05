# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-06

### Added

- **Configuration file support** — load settings from `pyproject.toml` (`[tool.codex-maintainer]`),
  `.codex-maintainer.toml`, or `~/.config/codex-maintainer/config.toml`
- **`stale` command** — list issues with no recent activity; optionally apply a label, post a
  comment, or close them; supports `--dry-run` to preview without making changes
- **`--repo` / `-r` flag** on all commands — override the target GitHub repository at runtime
- **`CODEX_MAINTAINER_MODEL` environment variable** — set the default OpenAI model for all commands
- **Per-command model config keys** — `review_model`, `triage_model`, `changelog_model`,
  `release_model` in the config file

### Changed

- All commands now resolve model and repository from config/env before falling back to defaults
- `mypy` target bumped from `python_version = "3.9"` to `"3.10"` (mypy no longer supports 3.9)

### Fixed

- Pre-existing `ruff` E501 line-length violations in `changelog.py`, `release.py`, `review.py`,
  and `triage.py`
- Missing type annotations (`dict` → `dict[str, Any]`) in `stale.py`, `triage.py`, `review.py`
- `json.loads()` return-type narrowing via `cast` to satisfy strict mypy

## [0.1.0] - 2026-06-05

### Added

- **`review` command** — fetch a PR diff and generate AI code review with OpenAI; optionally post
  the review as a GitHub PR comment
- **`triage` command** — classify, prioritize, and label a GitHub issue using OpenAI; outputs type,
  priority, complexity, suggested action, and label recommendations
- **`changelog` command** — generate a Keep-a-Changelog–formatted section from git commit history
- **`release` command** — generate user-friendly release notes for a new version tag
- GitHub Actions CI workflow (`ci.yml`) — lint, type-check, and test on Python 3.9–3.12
- Automated triage workflow (`auto-triage.yml`) and review workflow (`auto-review.yml`)

[0.2.0]: https://github.com/Haruhi-beeeep/codex-maintainer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Haruhi-beeeep/codex-maintainer/releases/tag/v0.1.0
