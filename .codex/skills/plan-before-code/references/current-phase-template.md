# Current Phase Template

Use after `phase-plan.md` is approved. Write the contract and story map for the
current phase only. Do not prepare future phases, create epics, create Beads, or
invent task IDs.

```markdown
# Phase Contract: Phase <N> - <Name>

**Feature slug:** <slug>
**Source of truth:** `history/<feature>/CONTEXT.md`
**Phase plan:** `history/<feature>/phase-plan.md`

## Entry State

<Observable truth before this phase starts.>

## Exit State

<Testable truth after this phase completes.>

## Demo / Proof

- <walkthrough, command, screenshot, or manual check>

## Stories

| Story | What Happens | Unlocks | Done When |
|---|---|---|---|
| S1 | <end-to-end user/system outcome> | <next outcome> | <observable done state> |

## Boundaries

**Out:** <not included in this phase>
**Success:** <signal to proceed>
**Pivot:** <signal to revise the plan>
```

```markdown
# Story Map: Phase <N> - <Name>

**Feature slug:** <slug>
**Phase contract:** `history/<feature>/phase-<n>-contract.md`

## Dependency Diagram

Entry -> Story 1 -> Story 2 -> Exit

## Story Table

| Story | Outcome | Contributes To | Creates | Done |
|---|---|---|---|---|
| S1 | <outcome> | <phase exit state> | <file, behavior, or check> | <done proof> |

## Story-To-Work-Plan Mapping

| Story | Work Plan Step | Proof |
|---|---|---|
| S1 | Step <N> | <validation/proof> |
```
