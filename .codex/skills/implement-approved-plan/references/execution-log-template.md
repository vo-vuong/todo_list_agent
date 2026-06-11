# Execution Log Template

Write this to `history/<feature-slug>/execution-log.md` during or after
implementation. Keep it factual and resumable.

```markdown
# <Feature Name> - Execution Log

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Current work:** <one sentence>
**Plan:** `history/<feature>/work-plan.md`
**Validation:** `history/<feature>/validation.md`

## Files Changed

- `<path>` - <what changed and why>

## Decisions Honored

| Decision | How implementation honored it |
|---|---|
| D1 | <behavior or file evidence> |

## Implementation Notes

- <important detail, tradeoff, or pattern followed>

## Deviations From Plan

- <none, or deviation with reason and whether it needs re-approval>

## Verification

| Command / Check | Result | Notes |
|---|---|---|
| `<command>` | PASS / FAIL / SKIPPED | <output summary or reason> |

## Remaining Work

- <none, or specific unfinished item>

## Handoff

Ready for `$review-after-code`: yes | no
```
