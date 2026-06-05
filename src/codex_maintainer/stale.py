"""Stale issue command: identify and manage issues with no recent activity."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, cast

from rich.console import Console
from rich.table import Table

console = Console()

_DEFAULT_COMMENT = (
    "This issue has had no activity for a while and has been marked as stale. "
    "It will be closed automatically if there is no further activity. "
    "Feel free to comment if this is still relevant!"
)


def _list_open_issues(repo: Optional[str]) -> list[dict[str, Any]]:
    cmd = [
        "gh", "issue", "list",
        "--state", "open",
        "--json", "number,title,labels,updatedAt,author,url",
        "--limit", "200",
    ]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return cast(list[dict[str, Any]], json.loads(result.stdout))


def _add_label(issue_number: int, label: str, repo: Optional[str]) -> None:
    cmd = ["gh", "issue", "edit", str(issue_number), "--add-label", label]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, check=True)


def _post_comment(issue_number: int, body: str, repo: Optional[str]) -> None:
    cmd = ["gh", "issue", "comment", str(issue_number), "--body", body]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, check=True)


def _close_issue(issue_number: int, repo: Optional[str]) -> None:
    cmd = ["gh", "issue", "close", str(issue_number)]
    if repo:
        cmd += ["--repo", repo]
    subprocess.run(cmd, check=True)


def _filter_stale(issues: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = []
    for issue in issues:
        updated = issue.get("updatedAt", "")
        try:
            updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        except ValueError:
            continue
        if updated_dt < cutoff:
            result.append(issue)
    return result


def run_stale(
    days: int,
    label: Optional[str],
    comment: bool,
    close: bool,
    repo: Optional[str],
    comment_body: str = _DEFAULT_COMMENT,
    dry_run: bool = False,
) -> None:
    with console.status("Fetching open issues..."):
        try:
            issues = _list_open_issues(repo)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]GitHub CLI error:[/red] {e.stderr.strip()}")
            raise SystemExit(1)

    stale = _filter_stale(issues, days)

    if not stale:
        console.print(f"[green]No stale issues found (inactive for {days}+ days).[/green]")
        return

    table = Table(
        title=f"Stale Issues — no activity for {days}+ days",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="cyan", width=6)
    table.add_column("Title")
    table.add_column("Last Updated", width=12)
    table.add_column("Labels")

    for issue in stale:
        issue_labels = ", ".join(lb["name"] for lb in issue.get("labels", []))
        updated = issue.get("updatedAt", "")[:10]
        table.add_row(str(issue["number"]), issue["title"], updated, issue_labels)

    console.print(table)
    console.print(f"\nFound [bold]{len(stale)}[/bold] stale issue(s).")

    if not (label or comment or close):
        return

    if dry_run:
        console.print("\n[yellow]Dry run — no changes made.[/yellow]")
        return

    console.print()
    success = 0
    for issue in stale:
        num = issue["number"]
        try:
            if label:
                _add_label(num, label, repo)
            if comment:
                _post_comment(num, comment_body, repo)
            if close:
                _close_issue(num, repo)
            console.print(f"  [green]✓[/green] #{num}")
            success += 1
        except subprocess.CalledProcessError as e:
            console.print(f"  [red]✗[/red] #{num}: {e.stderr.strip()}")

    if label:
        console.print(f"\n[green]Label '{label}' applied to {success} issue(s).[/green]")
    if comment:
        console.print(f"[green]Comment posted to {success} issue(s).[/green]")
    if close:
        console.print(f"[green]{success} issue(s) closed.[/green]")
