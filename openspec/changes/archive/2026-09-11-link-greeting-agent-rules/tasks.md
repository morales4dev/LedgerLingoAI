# Tasks: Link Greeting Module Agent Rules

- [x] Update `ai-specs/AGENTS.md` with the backend and greeting-module directory map. Verify the section names the local rule file and says it must be read before greeting-module work.
- [x] Add the relative Markdown link from `ai-specs/AGENTS.md` to `../backend/src/greeting/AGENTS.md`. Verify the target exists and resolves from the source file's directory.
- [x] Review nearby documentation for stale or contradictory agent-rule pointers. Verify no duplicate CrewAI guidance is introduced and no product files are changed.
- [x] Validate the completed change with `openspec validate link-greeting-agent-rules --type change` when the CLI is available, plus a repository-relative link check.
- [x] Add a short repository-rules section to `backend/src/greeting/AGENTS.md` linking back to `../../../ai-specs/AGENTS.md`. Verify the reverse link resolves, the local file does not duplicate the constitution, and no product files are changed.
