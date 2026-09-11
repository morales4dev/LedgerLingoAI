# Design: Link Greeting Module Agent Rules

## Approach

Add a short directory map to `ai-specs/AGENTS.md` near the canonical OS tree and load-skills guidance. The map will identify `backend/src/` as the backend surface and `backend/src/greeting/` as the CrewAI greeting module. Its local-rules entry will use this link:

```markdown
[backend/src/greeting/AGENTS.md](../backend/src/greeting/AGENTS.md)
```

The surrounding instruction should say that the local file is required context before editing or otherwise working on that module. This makes the relationship discoverable to both Markdown readers and assistants that follow links, while retaining the existing hierarchy in which the nearest `AGENTS.md` governs the module.

Add a short repository-rules section to `backend/src/greeting/AGENTS.md` with this link:

```markdown
[general agent constitution](../../../ai-specs/AGENTS.md)
```

This makes the rule relationship navigable in both directions without copying repository-wide policy into the CrewAI-specific file. The general constitution remains the repository-wide source of truth, while the greeting file remains the source of truth for CrewAI guidance.

## Compatibility

- The link is relative to `ai-specs/AGENTS.md`, so it must begin with `../`.
- The reverse link is relative to `backend/src/greeting/AGENTS.md`, so it must be `../../../ai-specs/AGENTS.md`.
- The change remains compatible with assistants that do not support `@` pointer syntax because it uses standard Markdown.
- No behavior depends on Markdown rendering or on a runtime loader.

## Verification

1. Resolve the Markdown link from the directory containing `ai-specs/AGENTS.md` and confirm it points to the existing greeting rules file.
2. Confirm the updated general file names the greeting module and requires its local rules before work there.
3. Resolve the reverse Markdown link from the greeting rules file and confirm it points to the existing general constitution.
4. Confirm neither rule file duplicates the other's guidance and no product files are changed.
5. Run `openspec validate link-greeting-agent-rules --type change` when the OpenSpec CLI is available.
