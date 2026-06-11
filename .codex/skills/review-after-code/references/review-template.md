# Review Template

Write this to `history/<feature-slug>/review.md`. Keep findings evidence-based
and serial; do not create review Beads or spawn review agents.

```markdown
# <Feature Name> - Review

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Current work:** <one sentence>
**Execution log:** `history/<feature>/execution-log.md`

## Summary

- P1: <count>
- P2: <count>
- P3: <count>
- Review decision: PASS | PASS WITH NON-BLOCKING FINDINGS | BLOCKED

## Findings

| Severity | Area | File / Line | Finding | Smallest Fix |
|---|---|---|---|---|
| P1/P2/P3 | code-quality/security/architecture/test-coverage | `<path>:<line>` | <issue and failure scenario> | <fix> |

## Artifact Verification

| Artifact / Behavior | EXISTS | SUBSTANTIVE | WIRED | Evidence |
|---|---|---|---|---|
| <artifact> | yes/no | yes/no | yes/no | <file/command/check> |

## Decision Coverage

| Decision | Evidence | Result |
|---|---|---|
| D1 | <file/test/UAT evidence> | PASS / FAIL |

## UAT Items

| Item | Decision | Prompt | Result | Reason If Skipped |
|---|---|---|---|---|
| 1 | D1 | <what user should confirm> | PASS / FAIL / SKIPPED | <reason> |

## Quality Gates

| Command / Check | Result | Notes |
|---|---|---|
| `<command>` | PASS / FAIL / SKIPPED | <summary> |

## Next Route

Next phase via `$plan-before-code` | `$capture-learnings` | fix P1 and rerun review
```
