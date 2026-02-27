"""Built-in skill lifecycle tools."""

from __future__ import annotations

from kai import Tool, ToolResult
from pydantic import BaseModel, Field, PrivateAttr

from kcastle.skills import SkillManager


class _SkillTool(Tool):
    _manager: SkillManager = PrivateAttr()

    @classmethod
    def for_manager(cls, manager: SkillManager) -> _SkillTool:
        tool = cls.model_construct()
        tool._manager = manager
        return tool


class ListSkillsTool(_SkillTool):
    name: str = "list_skills"
    description: str = "List discovered skills across builtin, user, and project layers."

    class Params(BaseModel):
        query: str = Field(default="", description="Optional search query.")
        max_results: int = Field(default=50, ge=1, le=500, description="Result cap.")

    async def execute(self, params: ListSkillsTool.Params) -> ToolResult:
        if params.query.strip():
            matches = self._manager.search(params.query)
            rows = [
                f"{m.meta.id} | {m.meta.source} | score={m.score:.2f} | {m.meta.description}"
                for m in matches[: params.max_results]
            ]
            return ToolResult(output="\n".join(rows) if rows else "(no matches)")

        rows = [
            f"{s.id} | {s.source} | {s.description}"
            for s in self._manager.all_skills()[: params.max_results]
        ]
        return ToolResult(output="\n".join(rows) if rows else "(no skills)")


class CreateSkillTool(_SkillTool):
    name: str = "create_skill"
    description: str = "Create a new anthropics-style skill with SKILL.md frontmatter."

    class Params(BaseModel):
        skill_id: str = Field(description="Unique skill ID (directory name).")
        name: str | None = Field(default=None, description="Skill name in frontmatter.")
        description: str = Field(description="When to use this skill (frontmatter description).")
        tags: list[str] = Field(default_factory=list, description="Skill tags.")
        instructions: str = Field(default="", description="Markdown instruction body.")
        target: str = Field(
            default="user",
            description="Target layer. Agent-managed skills use user.",
        )

    async def execute(self, params: CreateSkillTool.Params) -> ToolResult:
        try:
            if params.target != "user":
                return ToolResult.error("Agent-managed skill creation only supports target='user'")
            meta = self._manager.create_skill(
                params.skill_id,
                name=params.name,
                description=params.description,
                tags=params.tags,
                instructions=params.instructions,
                target=params.target,
            )
            return ToolResult(output=f"Created skill {meta.id} at {meta.file_path}")
        except Exception as e:
            return ToolResult.error(str(e))


class UpdateSkillTool(_SkillTool):
    name: str = "update_skill"
    description: str = "Update an existing skill's frontmatter or instruction body."

    class Params(BaseModel):
        skill_id: str = Field(description="Skill ID to update.")
        name: str | None = Field(default=None, description="New skill name.")
        description: str | None = Field(default=None, description="New description.")
        tags: list[str] | None = Field(default=None, description="New tags list.")
        instructions: str | None = Field(default=None, description="Replace instruction body.")
        append_instructions: str | None = Field(
            default=None,
            description="Append extra instructions to body.",
        )

    async def execute(self, params: UpdateSkillTool.Params) -> ToolResult:
        try:
            meta = self._manager.update_skill(
                params.skill_id,
                name=params.name,
                description=params.description,
                tags=params.tags,
                instructions=params.instructions,
                append_instructions=params.append_instructions,
            )
            return ToolResult(output=f"Updated skill {meta.id}")
        except Exception as e:
            return ToolResult.error(str(e))


def create_skill_lifecycle_tools(*, manager: SkillManager) -> list[Tool]:
    """Create built-in skill lifecycle tools."""
    return [
        ListSkillsTool.for_manager(manager),
        CreateSkillTool.for_manager(manager),
        UpdateSkillTool.for_manager(manager),
    ]
