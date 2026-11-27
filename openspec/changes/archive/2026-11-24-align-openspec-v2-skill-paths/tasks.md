# Tasks

## 1. Align Agent Guidance

- [x] 1.1 Update the two OpenSpec skill-path references in `ai-specs/AGENTS.md` to `.agents/skills/`; verify both reference the existing generated skill directory, no `.github/skills/` reference remains in that file, and the `ai-specs/skills/` guidance is unchanged.
- [x] 1.2 Update the OpenSpec design-rule path in `openspec/config.yaml` and quote the existing proposal rule containing `skip_specs: true`; verify `rtk openspec instructions proposal --change align-openspec-v2-skill-paths --json` returns all three proposal rules without a YAML mapping warning, and design instructions return the new path while schema, context, and cloud-agent settings remain unchanged.

## 2. Integration Verification

- [ ] 2.1 Run `rtk openspec validate align-openspec-v2-skill-paths --type change` and verify it passes with specs skipped; run `rtk proxy .venv/bin/python -m pytest tests/unit` from `backend/` for the repository's offline unit quality gate and report any failures explicitly.
- [x] 2.2 Review the implementation diff against the pre-apply baseline and verify only the planned hunks in `ai-specs/AGENTS.md` and `openspec/config.yaml` were introduced, with no edits to generated skills, removed prompts, custom skills, application files, or product specs; verify `rtk git diff --check` passes.

## Workflow follow-up

- Keep the change open after apply. Archive only after a separate explicit user approval.
