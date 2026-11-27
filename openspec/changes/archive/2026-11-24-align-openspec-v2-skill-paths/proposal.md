# Proposal

## Why

OpenSpec 2.x has migrated this repository's generated workflows to `.agents/skills/`, but the agent constitution and OpenSpec design rule still direct assistants to `.github/skills/`. Aligning those references prevents future work from following a missing directory or reversing the migration.

## What Changes

- Update the canonical OpenSpec CLI skill location and load-skills instruction in `ai-specs/AGENTS.md` to `.agents/skills/`.
- Update the corresponding design rule in `openspec/config.yaml` to `.agents/skills/`.
- Quote the existing proposal rule containing `skip_specs: true` so YAML treats it as a string. The installed CLI currently warns that this item is a mapping and ignores all proposal rules; its wording and intended meaning remain unchanged.
- Keep custom project skills under `ai-specs/skills/`.

## Capabilities

### New Capabilities

None. This tooling-only change declares `skip_specs: true`.

### Modified Capabilities

None. Product behavior and requirements remain unchanged.

## Impact

Implementation touches only `ai-specs/AGENTS.md` and `openspec/config.yaml`. It corrects agent guidance and configuration parsing without changing application code, dependencies, APIs, or product specs.

The user's existing generated-file migration is a prerequisite state, not work to repeat or revert in this change.

## Non-goals

- Move, regenerate, rename, or customize generated OpenSpec skills.
- Restore the removed `.github/prompts/` command files.
- Change custom project skills, workflow profiles, schema, or cloud-agent settings.
- Expand agent policies, change application behavior, or add CI.
- Commit or archive automatically.
