"""kcastle.skills — Skill management for kcastle.

Discover, search, and load skills across three layers:
builtin (``kcastle/skills``), user (``~/.kcastle/skills``), and
project (``<root>/.skills``).
"""

from kcastle.skills.loader import LoadedSkill, SkillLoader
from kcastle.skills.manager import SkillManager
from kcastle.skills.resolver import SkillMatch, SkillResolver
from kcastle.skills.schema import SkillMeta, load_skill_meta, write_skill_md
from kcastle.skills.view import render_compact_skills

__all__ = [
    "LoadedSkill",
    "SkillLoader",
    "SkillManager",
    "SkillMatch",
    "SkillMeta",
    "SkillResolver",
    "load_skill_meta",
    "render_compact_skills",
    "write_skill_md",
]
