---
name: plan-before-code
description: "Use after clarify-before-code has produced and the user has approved history/<feature>/CONTEXT.md. Turns locked decisions into a Khuym-like lightweight planning flow without Beads or epic maps: choose the smallest work shape, write history/<feature>/approach.md, write either history/<feature>/work-plan.md for direct/small/spike work or history/<feature>/phase-plan.md for phase-shaped work, then prepare current phase artifacts and stop for user approval before implementation. Updates .khuym/state.json approval gates."
---

# Plan Before Code

Turn an approved `CONTEXT.md` into the smallest useful implementation shape. This skill keeps the useful Khuym planning behavior while removing Beads, swarming, subagents, and epic maps.

## Hard Gates

- Do not run before `history/<feature>/CONTEXT.md` exists.
- Do not plan against memory alone; read `CONTEXT.md`.
- Do not change locked decisions. If they are wrong or incomplete, return to `$clarify-before-code`.
- Do not edit code in this skill.
- Do not create Beads, bead-like IDs, worker graphs, swarms, or future-work task queues.
- Do not create epic maps. For larger or risky work, use a phase plan.
- Do not create one plan per locked decision. Map many decisions into the smallest honest work shape.
- Stop at each approval gate. Do not approve your own plan or phase.

## Resume First

At the start:

1. Read `.khuym/state.json` if present.
2. Read `history/<feature>/CONTEXT.md` from `focus` or from the user-provided feature.
3. If `approach.md`, `work-plan.md`, `phase-plan.md`, `phase-<n>-contract.md`, or `phase-<n>-story-map.md` already exists, read the relevant files before deciding whether to revise or continue.
4. If `approved_gates.context` is not true, ask the user to approve `CONTEXT.md` or return to `$clarify-before-code`.

## Flow

1. **Bootstrap**
   - Read `CONTEXT.md`.
   - Confirm no `Resolve Before Coding` question blocks planning.
   - Keep `CONTEXT.md` as the source of truth.

2. **Discovery**
   - Inspect the smallest useful set of files to understand current patterns.
   - Capture only repo reality that changes the implementation path.
   - Do not broaden scope beyond locked decisions.

3. **Mode Gate**
   - Choose the least workflow that protects the work:
     - `direct_task`: one obvious low-risk change.
     - `spike`: one unknown must be proven before implementation.
     - `small_change`: a few related edits with clear validation.
     - `standard_feature`: ordered user/system capability that needs observable phases.
     - `high_risk_feature`: cross-cutting or hard-to-reverse work that needs a phase plan and explicit proof.
   - For `standard_feature` and `high_risk_feature`, use phase-shaped work. Do not use epic maps.
   - Above `small_change`, record why smaller modes are insufficient.

4. **Approach**
   - Write `history/<feature>/approach.md` from `references/approach-template.md`.
   - Include repo reality, chosen mode, chosen shape, rejected smaller shapes, likely files, risks, decision coverage, and validation needs.

5. **Shape Artifact**
   - For `direct_task`, `spike`, or `small_change`, write `history/<feature>/work-plan.md` from `references/work-plan-template.md`.
   - For `standard_feature` or `high_risk_feature`, write `history/<feature>/phase-plan.md` from `references/phase-plan-template.md`.
   - A phase plan must use observable milestones, not architecture layers.
   - A phase plan must name the current phase to prepare next and defer later phases.

6. **Direct/Small Gate**
   - For direct, spike, or small work, update `.khuym/state.json` for work-plan review:
     ```json
     {
       "active_skill": "plan-before-code",
       "feature_slug": "<feature>",
       "mode": "direct_task | spike | small_change",
       "phase": "work-shape-review",
       "phase_number": 0,
       "approved_gates": {
         "context": true,
         "work_shape": false,
         "phase_plan": false,
         "execution": false,
         "review": false
       },
       "summary": "Work plan ready for <feature>.",
       "next_action": "Ask the user to approve work-plan.md before implementation.",
       "focus": "history/<feature>/work-plan.md",
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Planning complete for `<feature>`.
     Approach written to `history/<feature>/approach.md`.
     Work plan written to `history/<feature>/work-plan.md`.
     Approve this work plan before implementation? (yes / revise / show plan)
     ```

7. **Phase Plan Gate**
   - For `standard_feature` or `high_risk_feature`, update `.khuym/state.json` for phase-plan review:
     ```json
     {
       "active_skill": "plan-before-code",
       "feature_slug": "<feature>",
       "mode": "standard_feature | high_risk_feature",
       "phase": "phase-plan-review",
       "phase_number": 0,
       "approved_gates": {
         "context": true,
         "work_shape": false,
         "phase_plan": false,
         "execution": false,
         "review": false
       },
       "summary": "Phase plan ready for <feature>.",
       "next_action": "Ask the user to approve phase-plan.md before current phase prep.",
       "focus": "history/<feature>/phase-plan.md",
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Planning complete for `<feature>`.
     Approach written to `history/<feature>/approach.md`.
     Phase plan written to `history/<feature>/phase-plan.md`.
     Approve this phase plan before current phase prep? (yes / revise / show plan)
     ```

8. **Current Phase Prep**
   - Run only after the user approves `phase-plan.md`.
   - Update `.khuym/state.json` with `approved_gates.phase_plan = true`, `phase = "current-phase-prep"`, and `focus = "history/<feature>/phase-plan.md"`.
   - Select the current phase named in `phase-plan.md`.
   - Write `history/<feature>/phase-<n>-contract.md` and `history/<feature>/phase-<n>-story-map.md` from `references/current-phase-template.md`.
   - Write `history/<feature>/work-plan.md` from `references/work-plan-template.md` for the current phase only.
   - Update `.khuym/state.json` with `phase = "work-shape-review"`, `phase_number = <n>`, `approved_gates.work_shape = false`, `focus = "history/<feature>/work-plan.md"`, and `next_action = "Ask the user to approve current phase work-plan.md before implementation."`
   - Tell the user:
     ```text
     Current phase prepared for `<feature>`.
     Phase contract written to `history/<feature>/phase-<n>-contract.md`.
     Story map written to `history/<feature>/phase-<n>-story-map.md`.
     Current work plan written to `history/<feature>/work-plan.md`.
     Approve this current phase work plan before implementation? (yes / revise / show plan)
     ```

## Handoff

If the user approves `work-plan.md`, update `.khuym/state.json` with `approved_gates.work_shape = true`, `phase = "validation-ready"`, `next_action = "Invoke validate-before-code before implementation."`, and `focus = "history/<feature>/work-plan.md"`.

Validation may start only when:

- `history/<feature>/CONTEXT.md` exists.
- `history/<feature>/approach.md` exists.
- `history/<feature>/work-plan.md` exists.
- `.khuym/state.json` has `approved_gates.context = true`.
- `.khuym/state.json` has `approved_gates.work_shape = true`.
- If the mode is `standard_feature` or `high_risk_feature`, `history/<feature>/phase-plan.md`, `phase-<n>-contract.md`, and `phase-<n>-story-map.md` also exist, and `.khuym/state.json` has `approved_gates.phase_plan = true`.

Implementation may start only after `$validate-before-code` writes `history/<feature>/validation.md` and `.khuym/state.json` has `approved_gates.execution = true`.

Anti-patterns: coding inside this skill, changing locked decisions instead of returning to clarify, Beads, bead-like task IDs, swarming, epic maps, one plan per decision, technical-bucket phases, oversized plans, future-work task graphs, or stale `.khuym/state.json`.

References: `references/approach-template.md`, `references/work-plan-template.md`, `references/phase-plan-template.md`, `references/current-phase-template.md`.
