---
name: validate-before-code
description: Use after plan-before-code has produced approved history/<feature>/work-plan.md and before any code edits. Validates the current work against repo reality, feasibility evidence, assumptions, integration readiness, and concrete verification. Writes history/<feature>/validation.md, updates .khuym/state.json, and stops for explicit execution approval. Does not use Beads, spawned agents, swarms, or epic maps.
---

# Validate Before Code

Validate the approved current work before source-code side effects. This is the single-agent, no-Beads equivalent of Khuym validating.

## Hard Gates

- Do not run before `history/<feature>/CONTEXT.md`, `approach.md`, and `work-plan.md` exist.
- Do not validate unless `.khuym/state.json` has `approved_gates.context = true` and `approved_gates.work_shape = true`.
- For phase-shaped work, require `approved_gates.phase_plan = true` and the current `phase-<n>-contract.md` / `phase-<n>-story-map.md`.
- Do not edit production code in this skill.
- Do not create Beads, bead-like IDs, spawned reviewers, or worker tasks.
- Do not proceed on plausibility. Require concrete evidence.
- Stop before execution and ask the user to approve it.

## Resume First

1. Read `.khuym/state.json`.
2. Read `history/<feature>/CONTEXT.md`, `approach.md`, and `work-plan.md`.
3. If present, read `phase-plan.md`, current phase contract, and current story map.
4. If `validation.md` already exists, read it before deciding whether to revise or continue.

## Flow

1. **Orient**
   - Identify mode, current work, current phase if any, files likely to change, and validation needs.
   - Confirm the work is still bounded by locked decisions.

2. **Reality Gate**
   - Check mode fit, repo fit, assumptions, smaller path, and proof surface.
   - Use file inspection, commands, tests, docs/version proof, or runtime probes.
   - Fail if the plan assumes nonexistent code, unsupported commands, hidden architecture work, or missing credentials.

3. **Feasibility Matrix**
   - Load `references/validation-template.md`.
   - Write `history/<feature>/validation.md`.
   - Record each assumption, risk, proof required, evidence, and result.
   - For `high_risk_feature`, include the matrix even when all assumptions look proven.

4. **Probe If Needed**
   - If one assumption can invalidate the current work, run a small yes/no probe.
   - Disposable proof may live in `.spikes/<feature>/`; do not wire spike code into production.
   - A `NO` result returns to `$plan-before-code`.

5. **Readiness Decision**
   - Use one result:
     - `READY`
     - `READY WITH CONSTRAINTS`
     - `NOT READY - RUN PROBE`
     - `NOT READY - RETURN TO PLANNING`
   - Update `validation.md` with the decision and evidence.

6. **State And Gate 3**
   - If ready, update `.khuym/state.json`; preserve the existing `approved_gates.phase_plan` value for direct/small work:
     ```json
     {
       "active_skill": "validate-before-code",
       "feature_slug": "<feature>",
       "phase": "execution-review",
       "mode": "<mode>",
       "current_work": "<current work>",
       "approved_gates": {
         "context": true,
         "work_shape": true,
         "phase_plan": true,
         "execution": false,
         "review": false
       },
       "summary": "Current work passed feasibility validation.",
       "next_action": "Ask the user to approve execution, then invoke implement-approved-plan.",
       "focus": "history/<feature>/validation.md",
       "blockers": [],
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Validation complete for `<feature>`.
     Validation written to `history/<feature>/validation.md`.
     Feasibility: READY | READY WITH CONSTRAINTS.
     Approve execution for this current work? (yes / revise / show validation)
     ```

## Handoff

If the user approves execution, update `.khuym/state.json` with `approved_gates.execution = true`, `phase = "implementation-approved"`, `next_action = "Invoke implement-approved-plan."`, and `focus = "history/<feature>/work-plan.md"`. Preserve the current `approved_gates.phase_plan` value.

If validation is not ready, update `.khuym/state.json` with `phase = "planning-revision-needed"`, `blockers` describing the failed proof, and `next_action = "Return to plan-before-code with validation.md."`

Anti-patterns: coding during validation, accepting "should work" as evidence, approving your own execution gate, Beads, spawned plan checkers, stale state, or validating future phases.

References: `references/validation-template.md`.
