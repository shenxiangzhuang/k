---
name: skill-creator
description: Create and evolve skills end-to-end when users ask to build a new skill, refactor an existing skill, add eval loops, or improve trigger accuracy via description tuning.
---

# skill-creator

Use this skill when the user asks to create, modify, optimize, benchmark, or operationalize a skill.

This is a core meta-skill. Prefer reusable structure over one-off edits.

## Operating rules

- Keep output concise and operational; avoid dumping long docs unless requested.
- Skill files must use `<skill-folder>/SKILL.md` with frontmatter `name` and `description`.
- Use stable lowercase-hyphen `name` values (`^[a-z0-9-]{1,64}$`) unless user explicitly overrides.
- Prefer user scope for agent-created skills: `~/.kcastle/skills/<skill-folder>/`.
- Treat project scope (`.skills`) as user-managed unless the user explicitly requests direct edits.
- Use bundled `scripts/` for repetitive deterministic tasks instead of repeating shell steps in prompts.
- Preserve existing intent during edits; prefer targeted patches over full rewrites.

## File map (read on demand)

| File | When to read |
|---|---|
| `references/workflow.md` | Creating or updating a skill |
| `references/evals.md` | Designing and running eval prompts |
| `references/description-optimization.md` | Tuning `description` for keyword matching |
| `references/templates.md` | Need JSON/markdown structure to produce |

Read only the file relevant to the current step.

## Workflow

1. **Intake**: Read `references/workflow.md`, follow the "Intake checklist" section.
2. **Author**: Draft or patch the skill per "Authoring rules" in the same file.
3. **Eval design**: Read `references/evals.md`, follow "Design evals" to write test prompts.
4. **Eval execution**: Follow "Run and review" in the same file to execute and grade.
5. **Trigger tuning**: Read `references/description-optimization.md` to improve keyword coverage.
6. **Iterate** until quality stabilizes or the user is satisfied.

## Self-evolution policy

When improving this `skill-creator` skill itself:

1. Keep orchestration in `SKILL.md` and move heavy detail into `references/`.
2. Add or refine templates before adding more prose.
3. Prefer changes that reduce ambiguity and increase repeatability.
4. Keep backward compatibility with current kcastle skill loading (`name` is the lookup key).

## Description optimization

Follow `references/description-optimization.md` and keep a clear before/after diff for `description`.

## Output contract

When finishing a creation/update cycle, report:

- Skill path modified
- What changed and why
- Suggested eval prompts
- Quality risks and next iteration focus
- Any assumptions or open questions
