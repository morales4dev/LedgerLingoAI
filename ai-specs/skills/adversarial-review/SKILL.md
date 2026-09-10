---
name: adversarial-review
description: Use when the user requests an adversarial review, red-team review, devil's advocate check, or independent verification pass before archiving an OpenSpec change.
version: 1.0.0
---

# adversarial-review Skill

Act as an **independent adversarial reviewer**: assume gaps, flaws, or unsafe behavior may exist until you have argued against them with evidence.

This skill is for the **verification window** of spec-driven development (after implementation, **before** archiving), when the human runs a **different agent or session** than the one that implemented the change.

Do **not** prescribe which agent, model, or IDE to use. That is the human's choice.

## Inputs

- Optional context from the user: OpenSpec change name, feature name, pull request URL or `owner/repo#number`.
- If missing, infer from the current session (active change, branch, or OpenSpec folder).

Resolve scope in this order: explicit change name → PR when given → current active work.

## Mindset

- Try to break the system, not only to confirm happy paths.
- Hunt incorrect assumptions about data shape, timing, ordering, authz, idempotency, and error handling.
- Trace cross-boundary risks: pieces that look fine in isolation but fail together.
- Treat the diff as incomplete context: missing tests, missing negative paths, or spec drift can hide issues.
- Calibrate depth to risk (secrets, privilege, data mutation, visitor-facing chat).

## Workflow

### Step 1 — Load the specification side first

1. Identify the OpenSpec change directory and read proposal, design, specs (if any), and `tasks.md`.
2. Extract acceptance criteria and explicit non-goals.
3. Note anything underspecified.

### Step 2 — Load the implementation side

1. If a PR was provided, treat it as the primary implementation surface. Map files to spec sections and tasks.
2. If no PR: use `git diff` against the merge base or the branch for the change.

### Step 3 — Adversarial pass

For each acceptance criterion or scenario:

1. State how the implementation could still fail while the author believed it passed.
2. Check negative and abuse cases where relevant.
3. Check tests: do they prove the criterion, or only the happy path?
4. Record spec vs code mismatches as first-class findings.

Do not treat other-project gates (mandatory curl, always-apply foreign skills, foreign ticket IDs) as Twin requirements. Twin verification is pytest units (no network), `openspec validate`, and the change's own tasks.

### Step 4 — Severity

- **Blocker**: incorrect behavior, security/privacy issue, or spec violation that should stop archive.
- **Major**: likely bug or significant gap; fix or spec update before archive.
- **Minor**: clarity or low-risk gap.
- **Question / assumption**: needs confirmation.

For each finding, state whether the fix belongs in code, tests, OpenSpec artifacts, or documentation.

### Step 5 — Verdict

- **PASS (adversarial)**: no blockers or majors; minors listed optionally.
- **PASS WITH GAPS**: minors only but tracked.
- **FAIL**: at least one blocker or major until addressed.

## Output format

```markdown
## Adversarial review

**Scope**: <change / PR>
**Sources**: <spec paths + PR or diff>

### Spec and task alignment
- ...

### Findings

| Severity | Area | Finding | Evidence | Suggested fix (code / spec / tests) |
|----------|------|---------|----------|--------------------------------------|
| Blocker / Major / Minor | | | | |

### Verdict
PASS | PASS WITH GAPS | FAIL

### Recommended next steps (before archive)
- ...
```

## Guardrails

- Do not praise implementation to balance criticism unless a strength directly mitigates a documented risk.
- Do not skip OpenSpec artifacts when they exist.
- If you cannot access the PR or diff, say so and list what is needed.
- This skill is Twin-owned. Do not symlink outside this repo.

## Completion

Always end with the verdict and whether archiving is **advisable** in the current state. Archive only after explicit user approval.
