"""Skill lifecycle management — discover, search, and load.

``SkillManager`` is the main entry point for all skill operations in kcastle.
It handles layered discovery (builtin → user → project), override resolution,
and prompt loading.
"""

from __future__ import annotations

import logging
from pathlib import Path

from kai import Tool

from kcastle.skills.loader import LoadedSkill, SkillLoader
from kcastle.skills.resolver import SkillMatch, SkillResolver
from kcastle.skills.schema import SkillMeta, load_skill_meta

_log = logging.getLogger("kcastle.skills")


def find_project_root(cwd: Path) -> Path:
    """Find the project root by walking up from *cwd*.

    Checks for ``.git/`` first, then ``pyproject.toml``, else returns *cwd*.
    """
    current = cwd.resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").is_dir():
            return parent
        if (parent / "pyproject.toml").is_file():
            return parent
    return current


class SkillManager:
    """Manages the skill runtime lifecycle: discover, search, and load.

    Skills are discovered from three layers (lowest → highest priority):
    1. Builtin skills (shipped with kcastle)
    2. User skills (``~/.kcastle/skills``)
    3. Project skills (``<project_root>/.skills``)

    Same-id skills in higher-priority layers override lower ones.
    """

    def __init__(
        self,
        *,
        user_skills_dir: Path,
        project_skills_dir: Path | None = None,
        builtin_skills_dir: Path | None = None,
    ) -> None:
        self._user_dir = user_skills_dir
        self._project_dir = project_skills_dir
        self._builtin_dir = builtin_skills_dir
        self._loader = SkillLoader()
        self._resolver = SkillResolver()
        self._skills: dict[str, SkillMeta] = {}

    # --- Discovery ---

    def discover(self) -> list[SkillMeta]:
        """Scan all skill layers and build the merged skill index.

        Override order: project > user > builtin (same id).
        Returns the final merged list of discovered skills.
        """
        merged: dict[str, SkillMeta] = {}

        # Layer 1: builtin (lowest priority)
        if self._builtin_dir and self._builtin_dir.is_dir():
            for meta in self._scan_dir(self._builtin_dir, "builtin"):
                merged[meta.id] = meta

        # Layer 2: user
        if self._user_dir.is_dir():
            for meta in self._scan_dir(self._user_dir, "user"):
                merged[meta.id] = meta

        # Layer 3: project (highest priority)
        if self._project_dir and self._project_dir.is_dir():
            for meta in self._scan_dir(self._project_dir, "project"):
                merged[meta.id] = meta

        self._skills = merged
        skills_list = list(merged.values())
        self._resolver.index(skills_list)
        _log.info("Discovered %d skills", len(skills_list))
        return skills_list

    # --- Search ---

    def search(self, query: str) -> list[SkillMatch]:
        """Search for skills matching the query."""
        return self._resolver.search(query)

    def all_skills(self) -> list[SkillMeta]:
        """Return all discovered skills."""
        return list(self._skills.values())

    def get_skill(self, skill_id: str) -> SkillMeta | None:
        """Get a single skill by ID."""
        return self._skills.get(skill_id)

    # --- Loading ---

    def load_skill(self, skill_id: str) -> LoadedSkill | None:
        """Load a skill (tools + prompt) by its ID."""
        meta = self._skills.get(skill_id)
        if meta is None:
            return None
        return self._loader.load(meta)

    def load_skills(self, skill_ids: list[str]) -> list[LoadedSkill]:
        """Load multiple skills by their IDs."""
        results: list[LoadedSkill] = []
        for sid in skill_ids:
            loaded = self.load_skill(sid)
            if loaded is not None:
                results.append(loaded)
        return results

    def collect_tools(self, loaded: list[LoadedSkill]) -> list[Tool]:
        """Flatten all tools from loaded skills.

        Skills are prompt-only in this architecture, so this generally returns
        an empty list. Kept for API compatibility.
        """
        return [tool for skill in loaded for tool in skill.tools]

    def collect_prompts(self, loaded: list[LoadedSkill]) -> str:
        """Concatenate instruction bodies from loaded skills."""
        fragments = [s.instructions for s in loaded if s.instructions]
        return "\n\n".join(fragments)

    # --- Internal ---

    @staticmethod
    def _scan_dir(directory: Path, source: str) -> list[SkillMeta]:
        """Scan a directory for skill sub-directories."""
        results: list[SkillMeta] = []
        if not directory.is_dir():
            return results
        for child in sorted(directory.iterdir()):
            if not child.is_dir():
                continue
            meta = load_skill_meta(child, source=source)
            if meta is not None:
                results.append(meta)
            else:
                _log.debug("Skipping %s — not a valid skill directory", child)
        return results
