---
name: review-after-code
description: Use after implement-approved-plan finishes the current work. Reviews the git diff and promised artifacts against history/<feature>/CONTEXT.md, approach.md, work-plan.md, validation.md, and execution-log.md. Writes history/<feature>/review.md, updates .khuym/state.json, blocks completion on P1 findings, and either routes to the next phase or capture-learnings. Does not use Beads, spawned review agents, swarms, or epic maps.
---

# Review After Code

Review completed current work before it is treated as done. This is the single-agent, serial equivalent of Khuym reviewing.

## Hard Gates

- Do not run before `history/<feature>/execution-log.md` exists.
- Do not rely on task closure as proof. Inspect the diff and artifacts.
- Do not create review Beads or spawned reviewers.
- P1 findings block completion until fixed or explicitly acknowledged by the user.
- UAT failures are not passes. Record skipped UAT with a reason.
- Do not mark `approved_gates.review = true` without user approval.

## Resume First

1. Read `.khuym/state.json`.
2. Read `CONTEXT.md`, `approach.md`, `work-plan.md`, `validation.md`, and `execution-log.md`.
3. Read phase artifacts if present.
4. Inspect the current git diff or changed files.
5. If `review.md` exists, read it before revising or rerunning review.

## Flow

1. **Diff Review**
   - Review serially across code quality, architecture, security, and test coverage.
   - Lead with concrete findings and cite file/line evidence.
   - Use severity:
     - `P1`: security breach, data loss, breaking change, production blocker, or locked decision broken.
     - `P2`: real reliability, architecture, performance, or important test gap.
     - `P3`: cleanup, docs, or future debt.

2. **Artifact Verification**
   - For promised artifacts and behavior, verify:
     - `EXISTS`
     - `SUBSTANTIVE`
     - `WIRED`
   - Missing or stub-only promised behavior is P1.
   - Exists and substantive but not wired is P2.

3. **Decision And UAT Check**
   - Map locked decisions to evidence in code, tests, screenshots, commands, or manual checks.
   - For SEE/CALL/RUN user-facing outcomes, present concise UAT items for user confirmation when needed.

4. **Review File**
   - Write `history/<feature>/review.md` from `references/review-template.md`.
   - Include findings, artifact verification, UAT items, quality gates, and next route.

5. **State And Gate 4**
   - If P1 findings exist, update `.khuym/state.json` with `phase = "review-blocked"`, `blockers`, `focus = "history/<feature>/review.md"`, and `next_action = "Fix P1 findings, then rerun review-after-code."`
   - If no P1 findings exist, update `.khuym/state.json`; preserve the existing `approved_gates.phase_plan` value for direct/small work:
     ```json
     {
       "active_skill": "review-after-code",
       "feature_slug": "<feature>",
       "phase": "review-ready",
       "approved_gates": {
         "context": true,
         "work_shape": true,
         "phase_plan": true,
         "execution": true,
         "review": false
       },
       "summary": "Review complete. No blocking P1 findings.",
       "next_action": "Ask the user to approve review, then route to next phase or capture-learnings.",
       "focus": "history/<feature>/review.md",
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Review complete for `<feature>`.
     Review written to `history/<feature>/review.md`.
     P1 blockers: <count>.
     Approve review result? (yes / fix P1 / show review)
     ```

## Handoff

If the user approves review, update `.khuym/state.json` with `approved_gates.review = true`.

- If `phase-plan.md` shows later phases still pending, set `phase = "planning-next-phase"`, `next_action = "Invoke plan-before-code for the next approved phase."`, and keep `focus = "history/<feature>/phase-plan.md"`.
- If the feature is complete, set `phase = "review-complete"`, `next_action = "Invoke capture-learnings."`, and `focus = "history/<feature>/review.md"`.

Anti-patterns: spawned reviewers, review Beads, ignoring P1, treating skipped UAT as pass, generic findings without evidence, or reviewing future phases.

References: `references/review-template.md`.
