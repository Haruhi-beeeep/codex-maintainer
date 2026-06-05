"""CLI entry point for codex-maintainer."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="codex-maintainer",
    help="AI-powered toolkit for OSS maintainers using OpenAI Codex.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

_REVIEW_MODEL_DEFAULT = "gpt-4.1"
_TRIAGE_MODEL_DEFAULT = "gpt-4.1-mini"
_CHANGELOG_MODEL_DEFAULT = "gpt-4.1"
_RELEASE_MODEL_DEFAULT = "gpt-4.1"

_REPO_HELP = "GitHub repo (owner/name). Defaults to current repo."
_MODEL_HELP = "OpenAI model to use."
_MODEL_OPT = typer.Option(None, "--model", "-m", envvar="CODEX_MAINTAINER_MODEL", help=_MODEL_HELP)
_REPO_OPT = typer.Option(None, "--repo", "-r", help=_REPO_HELP)


def _cfg_model(key: str, default: str) -> str:
    from codex_maintainer import config
    return str(config.get(key, config.get("model", default)))


def _cfg_repo() -> Optional[str]:
    from codex_maintainer import config
    val = config.get("repo")
    return str(val) if val else None


@app.command()
def review(
    pr: int = typer.Argument(..., help="Pull request number to review."),
    repo: Optional[str] = _REPO_OPT,
    model: Optional[str] = _MODEL_OPT,
    post: bool = typer.Option(False, "--post", help="Post the review as a GitHub PR comment."),
) -> None:
    """Review a pull request using OpenAI and post structured feedback."""
    from codex_maintainer.review import run_review
    resolved = model or _cfg_model("review_model", _REVIEW_MODEL_DEFAULT)
    run_review(pr, repo or _cfg_repo(), resolved, post)


@app.command()
def triage(
    issue: int = typer.Argument(..., help="Issue number to triage."),
    repo: Optional[str] = _REPO_OPT,
    model: Optional[str] = _MODEL_OPT,
    apply: bool = typer.Option(False, "--apply", help="Apply suggested labels to the issue."),
) -> None:
    """Triage a GitHub issue: classify, prioritize, and suggest labels."""
    from codex_maintainer.triage import run_triage
    resolved = model or _cfg_model("triage_model", _TRIAGE_MODEL_DEFAULT)
    run_triage(issue, repo or _cfg_repo(), resolved, apply)


@app.command()
def changelog(
    since: Optional[str] = typer.Option(
        None, "--since", "-s", help="Start tag/commit (default: latest git tag)."
    ),
    until: str = typer.Option("HEAD", "--until", "-u", help="End commit (default: HEAD)."),
    model: Optional[str] = _MODEL_OPT,
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write output to this file."),
) -> None:
    """Generate a CHANGELOG from git commit history."""
    from codex_maintainer.changelog import run_changelog
    resolved = model or _cfg_model("changelog_model", _CHANGELOG_MODEL_DEFAULT)
    run_changelog(since, until, resolved, output)


@app.command()
def release(
    tag: str = typer.Argument(..., help="New version tag (e.g. v1.2.0)."),
    since: Optional[str] = typer.Option(
        None, "--since", "-s", help="Previous tag to compare from."
    ),
    model: Optional[str] = _MODEL_OPT,
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write output to this file."),
) -> None:
    """Generate release notes for a new version."""
    from codex_maintainer.release import run_release
    resolved = model or _cfg_model("release_model", _RELEASE_MODEL_DEFAULT)
    run_release(tag, since, resolved, output)


@app.command()
def stale(
    days: int = typer.Option(
        90, "--days", "-d", help="Days of inactivity before an issue is considered stale."
    ),
    label: Optional[str] = typer.Option(
        None, "--label", "-l", help="Label to apply to stale issues."
    ),
    comment: bool = typer.Option(False, "--comment", help="Post a stale comment on each issue."),
    close: bool = typer.Option(False, "--close", help="Close each stale issue."),
    repo: Optional[str] = _REPO_OPT,
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print stale issues without making changes."
    ),
) -> None:
    """List (and optionally label/comment/close) issues with no recent activity."""
    from codex_maintainer import config
    from codex_maintainer.stale import _DEFAULT_COMMENT, run_stale

    resolved_days = days if days != 90 else int(config.get("stale_days", days))
    resolved_label = label or config.get("stale_label") or None
    resolved_comment_body = str(config.get("stale_comment", _DEFAULT_COMMENT))

    run_stale(
        days=resolved_days,
        label=resolved_label,
        comment=comment,
        close=close,
        repo=repo or _cfg_repo(),
        comment_body=resolved_comment_body,
        dry_run=dry_run,
    )


if __name__ == "__main__":
    app()
