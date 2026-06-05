"""Release command: generate release notes for a new version."""

from __future__ import annotations

import os
import subprocess
from typing import Optional

import openai
from rich.console import Console
from rich.markdown import Markdown

console = Console()

_SYSTEM_PROMPT = """\
You are an expert at writing engaging, user-friendly release notes for open source software.

Given git commits and a version number, write release notes that:
- Open with a brief paragraph summarizing what this release brings
- Group key changes by impact: Breaking Changes (if any) → Features → Fixes → Internal
- Use friendly, accessible language — rephrase commit messages in user terms
- Include a "How to upgrade" section if there are breaking changes
- Thank contributors by name if multiple authors are present

Format as Markdown. Be enthusiastic but professional."""


def _get_commit_log(since: Optional[str]) -> str:
    range_arg = f"{since}..HEAD" if since else "HEAD"
    cmd = ["git", "log", "--format=%an: %s%n%b---", range_arg]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def _get_contributors(since: Optional[str]) -> list[str]:
    range_arg = f"{since}..HEAD" if since else "HEAD"
    cmd = ["git", "log", "--format=%an", range_arg]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return sorted(set(result.stdout.strip().splitlines()))


def _get_previous_tag() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "HEAD^"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def run_release(tag: str, since: Optional[str], model: str, output: Optional[str]) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY is not set.")
        raise SystemExit(1)

    if since is None:
        since = _get_previous_tag()
        if since:
            console.print(f"Comparing from previous tag: [cyan]{since}[/cyan]")

    with console.status("Reading git history..."):
        try:
            commits = _get_commit_log(since)
            contributors = _get_contributors(since)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Git error:[/red] {e.stderr.strip()}")
            raise SystemExit(1)

    if not commits.strip():
        console.print("[yellow]No commits found.[/yellow]")
        return

    user_content = (
        f"Version: {tag}\n"
        f"Contributors: {', '.join(contributors)}\n\n"
        f"Commits:\n{commits}\n\n"
        f"Write release notes for version {tag}."
    )

    client = openai.OpenAI(api_key=api_key)

    with console.status(f"Generating release notes with {model}..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=2048,
        )

    notes = response.choices[0].message.content or ""

    console.print()
    console.print(Markdown(notes))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(notes + "\n")
        console.print(f"\n[green]Written to {output}[/green]")
