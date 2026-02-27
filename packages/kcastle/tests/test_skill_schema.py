from __future__ import annotations

from pathlib import Path

from kcastle.skills.schema import SkillMeta, load_skill_meta, write_skill_md


def test_load_skill_meta_requires_skill_md(tmp_path: Path) -> None:
    skill_dir = tmp_path / "legacy-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "skill.yaml").write_text("name: legacy\ndescription: old\n", encoding="utf-8")

    assert load_skill_meta(skill_dir, source="project") is None


def test_write_and_load_skill_md_roundtrip(tmp_path: Path) -> None:
    skill_dir = tmp_path / "new-skill"
    meta = SkillMeta(
        id="new-skill",
        name="new-skill",
        description="Do a specific workflow.",
        tags=["demo"],
        instructions="# New Skill\n\nUse tools first.",
        source="project",
        path=skill_dir,
        file_path=skill_dir / "SKILL.md",
    )

    write_skill_md(skill_dir, meta)
    loaded = load_skill_meta(skill_dir, source="project")

    assert loaded is not None
    assert loaded.id == "new-skill"
    assert loaded.description == "Do a specific workflow."
    assert "Use tools first." in loaded.instructions
