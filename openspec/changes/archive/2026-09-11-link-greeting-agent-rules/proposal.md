# Proposal: Link Greeting Module Agent Rules

## Why

The repository has CrewAI-specific instructions in `backend/src/greeting/AGENTS.md`, but the general agent constitution does not identify that local rule file. An assistant working from the repository-level guidance can miss the module-specific version and fail to apply its CrewAI freshness and documentation requirements.

## What Changes

- Add a project architecture and sub-module directory map to `ai-specs/AGENTS.md`.
- Add a relative Markdown link from the general rules file to `../backend/src/greeting/AGENTS.md`.
- Add a relative Markdown link from `backend/src/greeting/AGENTS.md` back to `../../../ai-specs/AGENTS.md` for repository-wide rules.
- State that the linked local rules must be read before making changes in the greeting module.
- Keep the local `backend/src/greeting/AGENTS.md` as the source of truth for CrewAI-specific guidance.

## Scope

This is an Agent OS documentation change only. It changes rule discovery and navigation; it does not change application behavior, CrewAI code, dependencies, or product specifications.

## Non-goals

- Do not duplicate the full CrewAI rules in `ai-specs/AGENTS.md`.
- Do not duplicate the repository constitution in `backend/src/greeting/AGENTS.md`; add only a navigation link back to it.
- Do not replace the nearest-directory `AGENTS.md` convention with a custom parser or runtime mechanism.
- Do not add an `@` directive unless the repository adopts a documented tool that interprets it.
- Do not modify `backend/src/greeting/AGENTS.md` as part of this change.
