---
name: clarify-before-code
description: Use when a coding request, feature idea, bug-fix intent, refactor, or implementation task is fuzzy enough that coding would require guessing. Clarifies requirements before planning or editing by asking one focused question at a time, locking user-facing decisions with stable IDs, writing decisions to history/<feature>/CONTEXT.md, and updating .khuym/state.json so future agents can reload context after interruption. Use especially when the user asks to confirm before starting, says the requirement is not clear yet, wants Socratic questioning, or wants Codex to clear the request before implementation while avoiding Beads and heavyweight Khuym machinery.
---

# Clarify Before Code

Turn fuzzy coding intent into locked decisions in `history/<feature>/CONTEXT.md`. This skill is the standalone equivalent of Khuym exploring: it clarifies, writes durable context, updates `.khuym/state.json`, and stops at a human approval gate before planning.

## Hard Gates

- Ask one question at a time; wait for the user before asking the next.
- Do not answer your own question.
- Do not edit code, create tasks, create Beads, or start implementation while decisions are still missing.
- Do not plan implementation here. Planning belongs in `$plan-before-code`.
- Do not keep decisions only in chat. Decisions must be written to `history/<feature>/CONTEXT.md`.
- Treat `history/<feature>/CONTEXT.md` as the source of truth once it exists.
- Stop at the context approval gate. Do not approve your own context.
- Keep `.khuym/state.json` consistent with the current feature, phase, focus file, and next action.

## Resume First

At the start of a clarification session:

1. Read `.khuym/state.json` if present.
2. If `focus` points to `history/<feature>/CONTEXT.md`, read that file before asking new questions.
3. If the user is continuing the same request, resume from the stored focus and open questions.
4. If the user starts a different request, create a new feature slug and update `.khuym/state.json` to point to the new context file.

If `.khuym/state.json` is missing, create it when writing the first `CONTEXT.md`. Do not require full Khuym onboarding.

## Flow

1. **Scope**
   - Classify: `Quick`, `Standard`, or `Risky`.
   - If the request spans independent outcomes, pick one primary outcome and defer the rest.
   - Choose a stable feature slug for `history/<feature-slug>/CONTEXT.md`.

2. **Domain**
   - Classify each applicable type:
     - `SEE`: UI, screen, visual state, user interaction.
     - `CALL`: API, CLI, SDK, webhook, integration contract.
     - `RUN`: job, script, worker, pipeline, runtime command.
     - `READ`: docs, logs, generated text, messages, reports.
     - `ORGANIZE`: data model, file layout, config, naming, taxonomy.
   - Load `references/decision-probes.md` and choose only relevant probes.

3. **Gray Areas**
   - Generate 1-4 unstated decisions that would make planning or implementation guess.
   - Do a quick local scout only when useful:
     ```bash
     rg "<feature-keyword>" src app packages tests docs --glob "*.{ts,tsx,js,jsx,py,md}"
     ```
   - Read a few relevant files and cite existing patterns in questions.
   - Exclude implementation preferences, performance tuning, and new scope unless they block the request.

4. **Socratic Locking**
   - Ask one concise question per message, preferably single-choice.
   - Start broad, then narrow into constraints.
   - After each answer, confirm the decision and assign a stable ID: `D1`, `D2`, `D3`.
   - For scope creep, mark it as deferred and return to the current question.

5. **Context Assembly**
   - Write `history/<feature-slug>/CONTEXT.md` from `references/context-template.md`.
   - Include boundary, domain types, locked decisions, scout paths, refs, open questions, validation proof, and deferred ideas.
   - Use concrete language. No placeholders, TODOs, or vague preferences.
   - If there are unresolved blockers, record them under `Open Questions` and keep `phase` as `clarifying`.

6. **State And Gate 1**
   - Update `.khuym/state.json`:
     ```json
     {
       "schema_version": "1.1",
       "active_skill": "clarify-before-code",
       "feature_slug": "<feature>",
       "mode": "Quick | Standard | Risky",
       "phase": "context-review",
       "approved_gates": {
         "context": false,
         "work_shape": false,
         "phase_plan": false,
         "execution": false,
         "review": false
       },
       "summary": "Clarification state for <feature>.",
       "next_action": "Ask the user to approve CONTEXT.md before invoking plan-before-code.",
       "focus": "history/<feature>/CONTEXT.md",
       "blockers": [],
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Tell the user:
     ```text
     Decisions captured. CONTEXT.md written to `history/<feature>/CONTEXT.md`.
     `.khuym/state.json` now points to the active context.
     Approve CONTEXT.md before planning? (yes / revise / show full CONTEXT.md)
     ```

## Handoff

If the user approves `CONTEXT.md`, update `.khuym/state.json` with `approved_gates.context = true`, `phase = "context-approved"`, and `next_action = "Invoke plan-before-code."` Then hand off:

```text
CONTEXT.md approved. Invoke `$plan-before-code` to create approach.md and the smallest work shape. It may write work-plan.md directly for small work, or phase-plan.md first for phase-shaped work.
```

Anti-patterns: chat-only decisions, bundled questions, implementation planning in this skill, Beads, swarming, code edits before `CONTEXT.md`, or stale `.khuym/state.json` after changing focus.

References: `references/decision-probes.md`, `references/context-template.md`.
