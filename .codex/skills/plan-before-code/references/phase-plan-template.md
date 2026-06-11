# Phase Plan Template

Write this to `history/<feature-slug>/phase-plan.md` only for
`standard_feature` or `high_risk_feature`. This replaces Khuym's epic-map path
with observable phases. Do not create epics, Beads, bead-like IDs, or future-work
task graphs.

```markdown
# <Feature Name> - Phase Plan

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Mode:** standard_feature | high_risk_feature
**Source of truth:** `history/<feature>/CONTEXT.md`

## Feature Summary

<2-4 sentences describing the outcome locked by CONTEXT.md.>

## Why Phase-Shaped Work

<Why direct_task, spike, and small_change are insufficient.>

## Decision Coverage

| Decision | Planning Impact | Phase |
|---|---|---|
| D1 | <what this decision changes> | Phase <N> |

## Phase Overview

| Phase | What Changes | Why Now | Demo / Proof | Unlocks |
|---|---|---|---|---|
| Phase 1 - <name> | <observable change> | <why first> | <check> | <next capability> |

## Order Check

- First phase is obvious because <reason>.
- Later phases build on earlier observable outcomes.
- No phase is just a technical bucket such as "backend", "frontend", or "tests".

## Current Phase To Prepare

Phase <N> - <name>

Why this phase is current:

<one concrete sentence>

## Deferred Phases

- Phase <N> - <name>: <why later>

## Approval

Phase plan approved: no
Current phase prep may start only after this changes to yes in the conversation
and `.khuym/state.json` has `approved_gates.phase_plan = true`.
```
