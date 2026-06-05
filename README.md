# codex-maintainer

**AI-powered toolkit for OSS maintainers using OpenAI Codex.**

[![CI](https://github.com/haruhi-abe/codex-maintainer/actions/workflows/ci.yml/badge.svg)](https://github.com/haruhi-abe/codex-maintainer/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/codex-maintainer.svg)](https://badge.fury.io/py/codex-maintainer)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

Maintaining an open source project means reviewing PRs, triaging issues, writing changelogs, and cutting releases — over and over. `codex-maintainer` automates the repetitive parts using OpenAI Codex so you can focus on what matters.

## Features

| Command | What it does |
|---|---|
| `codex-maintainer review <PR>` | AI code review with security, correctness, and style feedback |
| `codex-maintainer triage <issue>` | Classify, prioritize, and label GitHub issues automatically |
| `codex-maintainer changelog` | Generate a Keep-a-Changelog from git commit history |
| `codex-maintainer release <tag>` | Write release notes for a new version |
| `codex-maintainer stale` | List (and optionally label/comment/close) stale issues |

All commands work as a **CLI** and as **GitHub Actions** (drop-in workflows included).

## Installation

```bash
pip install codex-maintainer
```

Requires Python 3.9+ and an OpenAI API key.

## Quick Start

```bash
export OPENAI_API_KEY="sk-..."

# Review PR #42 and print feedback
codex-maintainer review 42

# Review and post the result as a GitHub comment
codex-maintainer review 42 --post

# Triage issue #7
codex-maintainer triage 7

# Triage and apply labels automatically
codex-maintainer triage 7 --apply

# Generate CHANGELOG since the last git tag
codex-maintainer changelog

# Generate release notes for v1.2.0
codex-maintainer release v1.2.0

# List issues inactive for 90+ days
codex-maintainer stale

# Label stale issues and post a comment (dry run first)
codex-maintainer stale --days 60 --label stale --comment --dry-run

# Apply for real
codex-maintainer stale --days 60 --label stale --comment
```

## GitHub Actions (zero config)

Copy the workflows from [`.github/workflows/`](.github/workflows/) into your repo:

**Auto-review every PR:**
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

Set `OPENAI_API_KEY` as a repository secret and you're done.

## Configuration

### Config file

Add a `[tool.codex-maintainer]` section to your `pyproject.toml`, or create a `.codex-maintainer.toml` in the project root:

```toml
# pyproject.toml
[tool.codex-maintainer]
model      = "gpt-4.1"        # default model for all commands
repo       = "owner/myrepo"   # default GitHub repo
stale_days = 60               # days before an issue is stale
stale_label = "stale"         # label applied by `stale --label`
# stale_comment = "Custom message..."
```

CLI flags always take precedence over the config file.

### Environment variables

`CODEX_MAINTAINER_MODEL` overrides the model for every command:

```bash
export CODEX_MAINTAINER_MODEL=gpt-4.1-mini
```

### Per-command flags

All commands accept `--model` and `--repo`:

```bash
codex-maintainer review 42 --model gpt-4.1
codex-maintainer triage 7  --model gpt-4.1-mini
codex-maintainer review 42 --repo myorg/myrepo
```

## Why codex-maintainer?

OSS maintainers spend significant time on mechanical work: reading PRs for obvious issues, labeling duplicate issues, formatting changelogs. This cognitive overhead compounds with project scale. `codex-maintainer` handles these tasks consistently and instantly, reducing maintainer burnout and improving response times for contributors.

It is designed to be **composable** — each command is independently useful as a CLI tool or as a GitHub Actions step — and **transparent** — the AI output is always shown to the maintainer before any action is taken (unless `--post`/`--apply` is explicitly set).

## Contributing

Contributions are welcome. Please open an issue first to discuss significant changes.

```bash
git clone https://github.com/haruhi-abe/codex-maintainer
cd codex-maintainer
pip install -e ".[dev]"
pytest tests/
```

## License

MIT — see [LICENSE](LICENSE).
