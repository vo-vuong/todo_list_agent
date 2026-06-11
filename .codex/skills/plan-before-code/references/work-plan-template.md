# Work Plan Template

Write this to `history/<feature-slug>/work-plan.md` after `CONTEXT.md` is
approved. For phase-shaped work, write it only after `phase-plan.md` is approved
and only for the current phase. Keep it implementation-ready. Do not create
Beads, bead-like IDs, epic maps, or future-work task graphs.

```markdown
# <Feature Name> - Work Plan

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Mode:** direct_task | spike | small_change | standard_feature | high_risk_feature
**Shape:** work-plan | current-phase-work-plan
**Phase:** none | Phase <N> - <name>
**Source of truth:** `history/<feature>/CONTEXT.md`

## Approved Context

- CONTEXT.md approved: yes
- Phase plan approved: yes | no | not required
- Current work approved: no

## Decision Coverage

| Decision | Required Behavior | Covered By |
|---|---|---|
| D1 | <behavior implied by the decision> | <step, validation, or out-of-scope note> |

## Current Work

<One concrete outcome to implement now.>

## Files Likely To Change

- `<path>` - <expected change>

## Implementation Steps

1. <small step>
2. <small step>
3. <small step>

## Validation

- <command, test, screenshot, or manual proof>

## Risks And Constraints

- <risk or constraint from CONTEXT.md, phase contract, or discovery>

## Out Of Scope

- <deferred idea, later phase, or adjacent work not included>

## Approval

Work plan approved: no
Implementation may start only after this changes to yes in the conversation
and `.khuym/state.json` has `approved_gates.work_shape = true`.
```
