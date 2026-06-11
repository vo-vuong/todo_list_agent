# Approach Template

Write this to `history/<feature-slug>/approach.md` after `CONTEXT.md` is approved
and before any shape artifact. Keep it evidence-based and small.

```markdown
# <Feature Name> - Approach

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Source of truth:** `history/<feature>/CONTEXT.md`

## Repo Reality

- `<path>` - <what exists today and why it matters>

## Chosen Mode And Shape

**Mode:** `direct_task | spike | small_change | standard_feature | high_risk_feature`
**Shape:** `work-plan | phase-plan`

Why this is the least workflow that protects the work:

<one concrete sentence>

Why smaller shapes are insufficient, if above `small_change`:

<one concrete sentence, or "Not applicable.">

## Decision Coverage

| Decision | Planning Impact | Covered By |
|---|---|---|
| D1 | <what it changes> | <work-plan step or phase> |

## Approach

<Short explanation of the implementation direction, grounded in locked decisions.>

## Likely Files

- `<path>` - <expected responsibility>

## Risks

- <risk, assumption, or ambiguity>

## Validation Needs

- <test, command, screenshot, manual proof, or spike result needed before done>

## Handoff

Use this approach plus the selected shape artifact before editing code. Do not
expand scope beyond `CONTEXT.md` without returning to clarification.
```
