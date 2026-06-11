---
name: capture-learnings
description: Use after review-after-code is approved or when work is intentionally abandoned with lessons worth keeping. Synthesizes durable project learnings from history/<feature>/CONTEXT.md, approach.md, work-plan.md, validation.md, execution-log.md, and review.md into history/learnings/YYYYMMDD-<feature>.md, optionally promotes only critical reusable rules to history/learnings/critical-patterns.md, and resets .khuym/state.json. Does not use Beads, spawned agents, CASS, or epic closeout.
---

# Capture Learnings

Capture reusable lessons after reviewed work. This is the single-agent, no-Beads equivalent of Khuym compounding.

## Hard Gates

- Do not fabricate learnings. Use only feature history, diffs, command output, review findings, or explicit user notes.
- Do not promote everything to `critical-patterns.md`; only promote high-signal rules likely to prevent future mistakes.
- Do not use Beads, spawned analysis agents, CASS, or external memory systems.
- Do not reset `.khuym/state.json` until the learning file is written.

## Resume First

1. Read `.khuym/state.json`.
2. Read available files under `history/<feature>/`: `CONTEXT.md`, `approach.md`, `phase-plan.md`, `work-plan.md`, `validation.md`, `execution-log.md`, and `review.md`.
3. If some files are missing, use only current evidence and state that the learning is partial.

## Flow

1. **Reconstruct What Happened**
   - Summarize original intent, key decisions, chosen plan shape, validation result, implementation outcome, and review outcome.

2. **Extract Learnings**
   - Identify:
     - reusable implementation patterns
     - decision rules that helped
     - failed assumptions or validation misses
     - workflow improvements for future features
   - Keep each learning concrete: situation, root cause, future rule.

3. **Write Learning File**
   - Create `history/learnings/YYYYMMDD-<feature>.md` from `references/learnings-template.md`.
   - Include evidence links to feature history files.

4. **Promote Critical Patterns**
   - Append to `history/learnings/critical-patterns.md` only when a learning is broadly reusable and failure-prone.
   - Do not duplicate an existing critical pattern.

5. **State Reset**
   - Update `.khuym/state.json`:
     ```json
     {
       "active_skill": "capture-learnings",
       "phase": "idle",
       "feature_slug": "",
       "summary": "Learning capture complete for <feature>.",
       "next_action": "",
       "focus": "",
       "blockers": [],
       "last_compounding_run": {
         "feature": "<feature>",
         "date": "YYYY-MM-DD",
         "learnings_file": "history/learnings/YYYYMMDD-<feature>.md",
         "critical_promotions": 0
       },
       "last_updated": "<ISO-8601 timestamp>"
     }
     ```
   - Delete `.khuym/HANDOFF.json` only if it is obsolete and belongs to this completed feature.

## Handoff

Tell the user:

```text
Learning capture complete.
- Learnings: `history/learnings/YYYYMMDD-<feature>.md`
- Critical promotions: <N>
State reset to idle.
```

Anti-patterns: generic lessons, critical-pattern spam, overwriting unrelated learnings, resetting active state before writing the learning file, or claiming evidence from memory without a local source.

References: `references/learnings-template.md`.
