"""Configuration loading for codex-maintainer.

Reads from (in priority order):
1. CLI flags (handled by the caller)
2. Environment variables (CODEX_MAINTAINER_MODEL, CODEX_MAINTAINER_REPO)
3. [tool.codex-maintainer] section in pyproject.toml
4. .codex-maintainer.toml in the current directory
5. ~/.config/codex-maintainer/config.toml
6. Hard-coded defaults
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional, cast

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        tomllib = None

_SENTINEL = object()
_cache: Optional[dict[str, Any]] = None


def _read_toml(path: Path) -> dict[str, Any]:
    if tomllib is None or not path.exists():
        return {}
    try:
        with open(path, "rb") as f:
            return cast(dict[str, Any], tomllib.load(f))
    except Exception:
        return {}


def _load() -> dict[str, Any]:
    # pyproject.toml [tool.codex-maintainer]
    data = _read_toml(Path("pyproject.toml"))
    section: dict[str, Any] = data.get("tool", {}).get("codex-maintainer", {})
    if section:
        return section

    # .codex-maintainer.toml in cwd
    local = _read_toml(Path(".codex-maintainer.toml"))
    if local:
        return local

    # ~/.config/codex-maintainer/config.toml
    global_cfg = _read_toml(Path.home() / ".config" / "codex-maintainer" / "config.toml")
    return global_cfg


def load() -> dict[str, Any]:
    """Return the merged config dict (cached for the process lifetime)."""
    global _cache
    if _cache is None:
        _cache = _load()
    return _cache


def get(key: str, default: Any = None) -> Any:
    """Get a config value by key, returning *default* if not set."""
    return load().get(key, default)
