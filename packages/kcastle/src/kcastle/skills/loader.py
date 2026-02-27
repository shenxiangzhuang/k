"""Skill loading for anthropics-style skills.

Skills are prompt-first: ``SKILL.md`` frontmatter + markdown body.
Executable runtime tools are provided globally by kcastle.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from kai import Tool

from kcastle.skills.schema import SkillMeta

_log = logging.getLogger("kcastle.skills")


# ---------------------------------------------------------------------------
# LoadedSkill
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LoadedSkill:
    """A skill loaded into memory — tools extracted, prompt ready."""

    meta: SkillMeta
    tools: list[Tool] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    instructions: str = ""


# ---------------------------------------------------------------------------
# SkillLoader
# ---------------------------------------------------------------------------


class SkillLoader:
    """Loads skills from their directories into ``LoadedSkill`` instances."""

    def load(self, meta: SkillMeta) -> LoadedSkill:
        """Load a single skill by metadata.

        In the minimalist architecture, skill-provided python tools are not
        dynamically imported; only prompt fragments are loaded.
        """
        return LoadedSkill(
            meta=meta,
            tools=[],
            instructions=meta.instructions,
        )
