"""Skill metadata schema and validation.

Canonical format follows anthropics/skills exactly:

- ``<skill-dir>/SKILL.md`` (required)
- YAML frontmatter with ``name`` and ``description`` (required)
- Markdown body as instructions
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

_log = logging.getLogger("kcastle.skills")


_SKILL_MD = "SKILL.md"


def _load_yaml_text(text: str) -> dict[str, Any]:
    """Parse YAML text with PyYAML."""
    import yaml  # type: ignore[import-untyped]

    data: object = yaml.safe_load(text)
    return dict(data) if isinstance(data, dict) else {}  # type: ignore[arg-type]


def _parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter and markdown body from ``SKILL.md``."""
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown.strip()

    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            payload = "\n".join(lines[1:idx])
            meta = _load_yaml_text(payload)
            body = "\n".join(lines[idx + 1 :]).strip()
            return meta, body
    return {}, markdown.strip()


def _slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9-]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "skill"


@dataclass(frozen=True, slots=True)
class SkillMeta:
    """Typed representation of a skill."""

    id: str
    """Unique skill identifier (defaults to directory name)."""

    name: str
    """Human-readable skill name."""

    description: str = ""
    """Short description of what this skill does."""

    tags: list[str] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    """Optional searchable tags."""

    instructions: str = ""
    """Instructions body loaded from ``SKILL.md``."""

    source: str = "unknown"
    """Source layer: ``builtin``, ``user``, or ``project``."""

    path: Path = field(default_factory=lambda: Path("."))
    """Absolute path to the skill directory."""

    file_path: Path = field(default_factory=lambda: Path(_SKILL_MD))
    """Absolute path to ``SKILL.md``."""


def load_skill_meta(skill_dir: Path, source: str = "unknown") -> SkillMeta | None:
    """Load a ``SkillMeta`` from a skill directory."""
    skill_md = skill_dir / _SKILL_MD
    if not skill_md.is_file():
        return None

    raw = skill_md.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)

    raw_name = str(frontmatter.get("name", "")).strip()
    name = _slugify(raw_name)
    if not raw_name:
        _log.warning("Skill %s missing name in SKILL.md frontmatter", skill_dir)
        return None

    description = str(frontmatter.get("description", "")).strip()
    if not description:
        _log.warning("Skill %s missing description in SKILL.md frontmatter", skill_dir)
        return None

    tags_raw: object = frontmatter.get("tags", [])
    tags = [str(t) for t in cast(list[object], tags_raw)] if isinstance(tags_raw, list) else []

    return SkillMeta(
        id=name,
        name=name,
        description=description,
        tags=tags,
        instructions=body,
        source=source,
        path=skill_dir.resolve(),
        file_path=skill_md.resolve(),
    )


def write_skill_md(skill_dir: Path, meta: SkillMeta) -> None:
    """Write anthropics-style ``SKILL.md`` for a skill."""
    skill_dir.mkdir(parents=True, exist_ok=True)
    fm: list[str] = ["---", f"name: {meta.name}", f"description: {meta.description}"]
    if meta.tags:
        fm.append("tags:")
        fm.extend(f"  - {tag}" for tag in meta.tags)
    fm.append("---")
    body = meta.instructions.strip()
    if body:
        content = "\n".join(fm) + "\n\n" + body + "\n"
    else:
        content = "\n".join(fm) + "\n\n# " + meta.name + "\n"
    (skill_dir / _SKILL_MD).write_text(content, encoding="utf-8")
