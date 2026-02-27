from __future__ import annotations

from pathlib import Path

from kcastle.skills.schema import SkillMeta
from kcastle.skills.view import extract_skill_hints, render_expanded_skills


def test_extract_skill_hints_normalizes_and_deduplicates() -> None:
    text = "Use $skill_creator then $skill-creator and also $skill-installer"
    assert extract_skill_hints(text) == ["skill-creator", "skill-installer"]


def test_render_expanded_skills_includes_instruction_body() -> None:
    meta = SkillMeta(
        id="skill-creator",
        name="skill-creator",
        description="Create skills",
        instructions="# creator\n\nDo things.",
        source="builtin",
        path=Path("/tmp/skill-creator"),
        file_path=Path("/tmp/skill-creator/SKILL.md"),
    )

    block = render_expanded_skills([meta])
    assert "<skill_expansion>" in block
    assert "[skill-creator] (builtin)" in block
    assert "Do things." in block
