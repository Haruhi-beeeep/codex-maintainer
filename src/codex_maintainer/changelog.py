"""Changelog command: generate CHANGELOG from git commit history."""

from __future__ import annotations

import os
import subprocess
from typing import Optional

import openai
from rich.console import Console
from rich.markdown import Markdown

console = Console()

_SYSTEM_PROMPT = """\
You are an expert at writing clear, user-focused changelogs in Keep a Changelog format.

Given git commit messages, generate a well-structured CHANGELOG section.

Group changes into these categories (only include non-empty ones):
- ### Added — new features
- ### Changed — changes in existing functionality
- ### Deprecated — soon-to-be removed features
- ### Removed — removed features
- ### Fixed — bug fixes
- ### Security — vulnerability fixes

Rules:
- Write from the user's perspective, not the developer's
- Skip purely internal commits (e.g. ci:, chore:, refactor: with no user impact)
- One line per change, starting with a capital letter
- Do not include commit hashes
- Output only the Markdown content with no preamble"""


def _get_git_log(since: Optional[str], until: str) -> str:
    range_arg = f"{since}..{until}" if since else until
    cmd = ["git", "log", "--format=%s%n%b---", range_arg]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def _get_latest_tag() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def run_changelog(since: Optional[str], until: str, model: str, output: Optional[str]) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY is not set.")
        raise SystemExit(1)

    if since is None:
        since = _get_latest_tag()
        if since:
            console.print(f"Using latest tag as base: [cyan]{since}[/cyan]")

    with console.status("Reading git history..."):
        try:
            commits = _get_git_log(since, until)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Git error:[/red] {e.stderr.strip()}")
            raise SystemExit(1)

    if not commits.strip():
        console.print("[yellow]No commits found in the specified range.[/yellow]")
        return

    client = openai.OpenAI(api_key=api_key)

    with console.status(f"Generating CHANGELOG with {model}..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Commits:\n\n{commits}"},
            ],
            max_tokens=2048,
        )

    changelog_text = response.choices[0].message.content or ""

    console.print()
    console.print(Markdown(changelog_text))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(changelog_text + "\n")
        console.print(f"\n[green]Written to {output}[/green]")
