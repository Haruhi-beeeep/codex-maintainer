# codex-maintainer

**AI-powered automation for OSS maintainers — review PRs, triage issues, and ship releases faster.**

[![CI](https://github.com/Haruhi-beeeep/codex-maintainer/actions/workflows/ci.yml/badge.svg)](https://github.com/Haruhi-beeeep/codex-maintainer/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/codex-maintainer.svg)](https://badge.fury.io/py/codex-maintainer)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The problem

OSS maintainers are burning out. The average maintainer of a mid-sized project spends **4–8 hours per week** on purely mechanical work:

- Reading PR diffs and writing the same feedback patterns again and again
- Labeling and prioritizing issues that follow obvious templates ("bug", "feature", "question")
- Formatting changelogs and release notes from git logs
- Chasing stale issues that contributors have abandoned

This overhead scales with project popularity — the more successful your project, the more time you lose to process. Many maintainers reduce responsiveness, close issues without review, or abandon projects entirely.

**`codex-maintainer` eliminates the mechanical layer** so maintainers can focus on architecture decisions, mentoring contributors, and the work only a human can do.

---

## What it does

| Command | Task automated |
|---|---|
| `codex-maintainer review <PR>` | Full AI code review — correctness, security, performance, test coverage — posted as a GitHub comment |
| `codex-maintainer triage <issue>` | Classifies type, priority, complexity, and suggests labels — applies them with `--apply` |
| `codex-maintainer changelog` | Generates a [Keep a Changelog](https://keepachangelog.com/) section from git history |
| `codex-maintainer release <tag>` | Writes user-facing release notes from commits and contributors |
| `codex-maintainer stale` | Finds inactive issues and optionally labels, comments, or closes them |

Every command works as a **one-shot CLI tool** and as a **GitHub Actions step** (drop-in workflow files included).

---

## Installation

```bash
pip install codex-maintainer
```

Requires Python 3.9+, an [OpenAI API key](https://platform.openai.com/api-keys), and the [GitHub CLI](https://cli.github.com/) (`gh`).

---

## Quick start

```bash
export OPENAI_API_KEY="sk-..."

# AI code review for PR #42
codex-maintainer review 42

# Post the review directly to GitHub
codex-maintainer review 42 --post

# Triage issue #7 and apply suggested labels
codex-maintainer triage 7 --apply

# Generate CHANGELOG since last tag
codex-maintainer changelog

# Release notes for v1.2.0
codex-maintainer release v1.2.0

# Preview stale issues without changes
codex-maintainer stale --days 60 --label stale --comment --dry-run

# Apply stale management for real
codex-maintainer stale --days 60 --label stale --comment
```

---

## GitHub Actions integration

Drop these workflow files into **any** GitHub repository. No code changes needed.

**AI review on every PR:**
```yaml
# .github/workflows/auto-review.yml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install codex-maintainer
      - run: codex-maintainer review ${{ github.event.pull_request.number }} --post
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Auto-triage every new issue:**
```yaml
# .github/workflows/auto-triage.yml
name: Auto Triage Issues
on:
  issues:
    types: [opened]
jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install codex-maintainer
      - run: codex-maintainer triage ${{ github.event.issue.number }} --apply
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Set `OPENAI_API_KEY` as a repository secret. That's it.

---

## Configuration

### Config file (optional)

```toml
# pyproject.toml
[tool.codex-maintainer]
model       = "gpt-4.1"       # default model for all commands
repo        = "owner/myrepo"  # default GitHub repo
stale_days  = 60              # days before an issue is considered stale
stale_label = "stale"         # label to apply
# stale_comment = "Custom stale message..."
```

Also supported: `.codex-maintainer.toml` in the project root, or `~/.config/codex-maintainer/config.toml` for global defaults.

### Priority order

CLI flags → `CODEX_MAINTAINER_MODEL` env var → config file → built-in defaults

---

## Why this matters for the OSS ecosystem

Open source software underpins virtually all modern infrastructure. Yet the humans who maintain it are **volunteers** whose time is the scarcest resource in the ecosystem.

Maintainer burnout has already caused critical vulnerabilities (left unchecked due to reviewer overload), broken build pipelines (from unmaintained dependencies), and the abandonment of projects depended on by millions of developers.

`codex-maintainer` addresses this by applying AI to exactly the tasks that consume maintainer time without requiring maintainer judgment:

- **Code review**: AI handles pattern recognition (unhandled errors, injection risks, missing tests) so the maintainer focuses on design feedback
- **Issue triage**: AI classifies incoming issues consistently, preventing triaging backlog from accumulating
- **Release automation**: AI drafts changelogs and release notes from raw git history, eliminating a recurring publication bottleneck

The tool is designed to be **adopted in minutes**, work with **any GitHub-hosted project**, and be **transparent** — all AI output is visible to the maintainer before any action is taken.

---

## Design principles

- **Composable**: each command is independently useful; use one or all
- **Non-destructive by default**: actions only happen when `--post`, `--apply`, or `--close` is explicitly passed; `--dry-run` is always available
- **Transparent**: AI output is printed before anything is posted to GitHub
- **Model-agnostic**: works with any OpenAI model; defaults tuned for cost/quality balance

---

## Contributing

```bash
git clone https://github.com/Haruhi-beeeep/codex-maintainer
cd codex-maintainer
pip install -e ".[dev]"
pytest tests/
```

Contributions welcome. Please open an issue to discuss significant changes.

---

## License

MIT — see [LICENSE](LICENSE).
