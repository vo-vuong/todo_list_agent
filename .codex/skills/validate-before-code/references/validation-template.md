# Validation Template

Write this to `history/<feature-slug>/validation.md`. Keep evidence concrete and
current-work scoped. Do not create Beads, spawned agents, or future-work tasks.

```markdown
# <Feature Name> - Validation

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Mode:** direct_task | spike | small_change | standard_feature | high_risk_feature
**Current work:** <one sentence>
**Source of truth:** `history/<feature>/CONTEXT.md`
**Plan:** `history/<feature>/work-plan.md`

## Reality Gate

| Check | Result | Evidence |
|---|---|---|
| Mode fit | PASS / FAIL | <file/command/reason> |
| Repo fit | PASS / FAIL | <file/command/reason> |
| Assumptions | PASS / FAIL | <file/command/reason> |
| Smaller path | PASS / FAIL | <file/command/reason> |
| Proof surface | PASS / FAIL | <file/command/reason> |

## Feasibility Matrix

| Part / Assumption | Risk | Proof Required | Evidence | Result |
|---|---|---|---|---|
| <part> | LOW / MEDIUM / HIGH | <proof> | <file, command, output, doc, or probe> | PASS / FAIL |

## Probes

- <none, or yes/no probe with result and constraints>

## Integration Readiness

- <how the current work can be wired without hidden architecture work>

## Verification Readiness

- <exact command, test, screenshot, or manual proof from work-plan.md>

## Decision

READY | READY WITH CONSTRAINTS | NOT READY - RUN PROBE | NOT READY - RETURN TO PLANNING

## Constraints For Implementation

- <constraint the implementer must obey>

## Approval

Execution approved: no
Implementation may start only after this changes to yes in conversation and
`.khuym/state.json` has `approved_gates.execution = true`.
```
