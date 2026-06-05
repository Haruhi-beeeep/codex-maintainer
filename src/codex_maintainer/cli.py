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


@app.command()
def review(
    pr: int = typer.Argument(..., help="Pull request number to review."),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="GitHub repo (owner/name). Defaults to current repo."),
    model: str = typer.Option("gpt-4.1", "--model", "-m", help="OpenAI model to use."),
    post: bool = typer.Option(False, "--post", help="Post the review as a GitHub PR comment."),
) -> None:
    """Review a pull request using OpenAI and post structured feedback."""
    from codex_maintainer.review import run_review
    run_review(pr, repo, model, post)


@app.command()
def triage(
    issue: int = typer.Argument(..., help="Issue number to triage."),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="GitHub repo (owner/name). Defaults to current repo."),
    model: str = typer.Option("gpt-4.1-mini", "--model", "-m", help="OpenAI model to use."),
    apply: bool = typer.Option(False, "--apply", help="Apply suggested labels to the issue."),
) -> None:
    """Triage a GitHub issue: classify, prioritize, and suggest labels."""
    from codex_maintainer.triage import run_triage
    run_triage(issue, repo, model, apply)


@app.command()
def changelog(
    since: Optional[str] = typer.Option(None, "--since", "-s", help="Start tag/commit (default: latest git tag)."),
    until: str = typer.Option("HEAD", "--until", "-u", help="End commit (default: HEAD)."),
    model: str = typer.Option("gpt-4.1", "--model", "-m", help="OpenAI model to use."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write output to this file."),
) -> None:
    """Generate a CHANGELOG from git commit history."""
    from codex_maintainer.changelog import run_changelog
    run_changelog(since, until, model, output)


@app.command()
def release(
    tag: str = typer.Argument(..., help="New version tag (e.g. v1.2.0)."),
    since: Optional[str] = typer.Option(None, "--since", "-s", help="Previous tag to compare from."),
    model: str = typer.Option("gpt-4.1", "--model", "-m", help="OpenAI model to use."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write output to this file."),
) -> None:
    """Generate release notes for a new version."""
    from codex_maintainer.release import run_release
    run_release(tag, since, model, output)


if __name__ == "__main__":
    app()
