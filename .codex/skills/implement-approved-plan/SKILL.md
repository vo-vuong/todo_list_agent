---
name: implement-approved-plan
description: Use after validate-before-code has passed and the user has explicitly approved execution for the current work. Implements the approved history/<feature>/work-plan.md in the main agent only, records history/<feature>/execution-log.md, runs verification, updates .khuym/state.json, and hands off to review-after-code.
---

# Implement Approved Plan

Implement one validated current work plan in the main agent. This replaces Khuym swarming plus executing with a single-agent execution loop.

## Hard Gates

- Do not run before `history/<feature>/validation.md` exists.
- Do not run unless `.khuym/state.json` has `approved_gates.execution = true`.
- Do not choose new work. Implement only `history/<feature>/work-plan.md`.
- Do not create Beads, spawn agents, reserve worker tasks, or split work into a swarm.
- Do not change locked decisions. If implementation needs a decision change, stop and return to `$clarify-before-code` or `$plan-before-code`.
- Do not leave verification unrun unless impossible; record any missed verification in `execution-log.md`.

## Resume First

1. Read `.khuym/state.json`.
2. Read `CONTEXT.md`, `approach.md`, `work-plan.md`, and `validation.md`.
3. If phase-shaped, read `phase-plan.md`, current phase contract, and story map.
4. If `execution-log.md` exists, read it and continue from recorded remaining work.

## Flow

1. **Enter Execution**
   - Update `.khuym/state.json` with `active_skill = "implement-approved-plan"`, `phase = "implementing"`, and `focus = "history/<feature>/work-plan.md"`.

2. **Implement**
   - Read each file before editing.
   - Follow the implementation steps in `work-plan.md`.
   - Keep the edit surface bounded to current work.
   - Match existing project patterns and validation constraints.
   - Avoid stubs, TODO-only code, dead code, and pseudo-implementations.

3. **Verify**
   - Run the validation commands/checks named in `work-plan.md` and `validation.md`.
   - Fix root causes and rerun when feasible.
   - After two serious failed attempts on the same blocker, stop and write the blocker to state.

4. **Execution Log**
   - Write or update `history/<feature>/execution-log.md` from `references/execution-log-template.md`.
   - Record files changed, decisions honored, deviations, verification commands, and remaining work.

5. **State And Handoff**
   - If implementation and verification are done, update `.khuym/state.json`:
     ```json
     {
       "active_skill": "implement-approved-plan",
       "feature_slug": "<feature>",
       "phase": "implemented",
       "summary": "Current work implemented and ready for review.",
       "next_action": "Invoke review-after-code.",
       "focus": "history/<feature>/execution-log.md",
       "blockers": [],
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Implementation complete for `<feature>`.
     Execution log written to `history/<feature>/execution-log.md`.
     Invoke `$review-after-code` before considering the work complete.
     ```

## Blocked Or Handoff

If blocked, update `.khuym/state.json` with `phase = "implementation-blocked"`, `blockers`, and `next_action` explaining whether to revise planning, rerun validation, or ask the user.

If context is close to exhaustion, write `.khuym/HANDOFF.json` with feature, current skill, files touched, completed steps, remaining steps, commands run, blockers, and next action.

Anti-patterns: implementing unapproved work, broad refactors, silent scope expansion, skipping verification, invented task IDs, spawned workers, or claiming completion without `execution-log.md`.

References: `references/execution-log-template.md`.
