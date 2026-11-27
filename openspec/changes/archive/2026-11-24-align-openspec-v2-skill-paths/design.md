# Design

## Context

See [proposal.md](./proposal.md) for motivation and scope. The repository already contains seven OpenSpec skills under `.agents/skills/`, and `.agents/skills/.openspec-target` identifies `github-copilot`. The generated `.github/skills/` and `.github/prompts/` files have been removed by the user's migration.

Two constitution references and one OpenSpec design-rule reference still use the former skill location. The current design rule conflicts with the migration and this explicit proposal request; the change updates that rule rather than moving skills back.

The installed CLI also reports that `rules.proposal[1]` is a YAML mapping because its unquoted text contains `: `. It consequently ignores the entire proposal-rule list.

## Goals / Non-Goals

**Goals:**

- Make both sources of agent guidance agree with the existing project-local OpenSpec 2.x layout.
- Preserve the distinction between generated OpenSpec skills and custom project skills.
- Preserve the intended proposal rules as valid YAML strings.

**Non-Goals:**

- Add discovery wrappers, symlinks, duplicate skill trees, or editor settings.
- Modify built-in skill instructions or historical archived artifacts.
- Reconfigure global skill installation or repeat the user's migration.

## Decisions

### Update the references in place

Replace `.github/skills/` with `.agents/skills/` only in the constitution's canonical-tree entry, its load-skills paragraph, and the matching config design rule. Retain all surrounding policy, including the separation from `ai-specs/skills/`.

Restoring the old skill tree would contradict OpenSpec 2.x's installed layout. Duplicating skills or adding an adapter would introduce unnecessary maintenance.

### Quote the malformed proposal rule without rewriting it

Wrap the entire existing scalar containing `skip_specs: true` in YAML quotes. Keep its text unchanged, and avoid reserializing the rest of the config. This restores the CLI's ability to load proposal rules without adding a policy or changing application behavior.

### Keep planning and application separate

The proposal has `skip_specs: true`; no delta or main product specs are created. Implementation requires explicit user approval. The existing migration changes remain untouched and must be distinguished from the two-file implementation diff during review.

## Risks / Trade-offs

- Existing migration changes could be mistaken for this change's edits -> Record the working-tree baseline before apply and review only the newly introduced hunks.
- A path replacement alone could leave config rules silently ignored -> Verify that the CLI returns all three proposal rules and no mapping warning after the quoting fix.
- Discoverable files do not guarantee every assistant follows them -> Confirm the referenced skill files exist; a fresh Copilot chat can separately verify editor discovery.

## Migration Plan

1. Obtain explicit approval to apply this plan.
2. Update the two constitution references.
3. Update the config design-rule path and quote the malformed proposal scalar.
4. Verify the exact references, unchanged custom-skill location, and CLI rule parsing; run change validation and the repository's offline unit gate.
5. Review the diff without regenerating skills, restoring prompts, committing, or archiving.

If rollback is needed, reverse only the approved documentation and config hunks. Preserve all user migration changes and planning artifacts.
