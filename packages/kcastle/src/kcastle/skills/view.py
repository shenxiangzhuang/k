"""Skill prompt rendering helpers."""

from __future__ import annotations

import re

from kcastle.skills.schema import SkillMeta

_HINT_RE = re.compile(r"\$([A-Za-z0-9_.-]+)")


def render_compact_skills(skills: list[SkillMeta]) -> str:
    """Render compact skill metadata for system prompt injection."""
    if not skills:
        return ""

    lines = ["<skills>"]
    for skill in skills:
        lines.append(f"- {skill.id} ({skill.source}): {skill.description}")
    lines.append("</skills>")
    return "\n".join(lines)


def extract_skill_hints(text: str) -> list[str]:
    """Extract unique ``$skill`` style hints from free text."""
    hints: list[str] = []
    seen: set[str] = set()

    for match in _HINT_RE.finditer(text):
        raw = match.group(1).strip().lower()
        if not raw:
            continue
        normalized = raw.replace("_", "-")
        if normalized in seen:
            continue
        seen.add(normalized)
        hints.append(normalized)

    return hints


def render_expanded_skills(skills: list[SkillMeta]) -> str:
    """Render full instruction bodies for explicitly hinted skills."""
    if not skills:
        return ""

    lines = ["<skill_expansion>"]
    for skill in skills:
        lines.append(f"=== [{skill.id}] ({skill.source}) ===")
        if skill.instructions.strip():
            lines.append(skill.instructions.strip())
        lines.append("")
    lines.append("</skill_expansion>")
    return "\n".join(lines).strip()
