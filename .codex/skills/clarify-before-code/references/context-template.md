# CONTEXT.md Template

Write this to `history/<feature-slug>/CONTEXT.md`. Remove unused optional sections.
No TODOs, placeholders, or vague decisions.

```markdown
# <Feature Name> - Context

**Feature slug:** <slug>
**Date:** YYYY-MM-DD
**Clarification status:** clarifying | complete
**Scope:** Quick | Standard | Risky
**Domain types:** SEE | CALL | RUN | READ | ORGANIZE

## Feature Boundary

<One concrete sentence describing what this work delivers and where it ends.>

## Locked Decisions

These are fixed. Implementation must follow them exactly.

- **D1:** <specific decision, not a preference>
  - Rationale: <optional, only if it changes implementation>
- **D2:** <specific decision>

### Agent's Discretion

<What the user delegated to the agent, with constraints. Remove if none.>

## Specific Ideas And References

- <Mockup/example/reference the user mentioned, and what it means.>

## Existing Code Context

From the quick scout. Future agents read these before implementation.

### Reusable Assets

- `<path>` - <what it does and how it applies>

### Established Patterns

- `<path>` - <pattern to preserve>

### Integration Points

- `<path>` - <what new work connects to>

## Validation

- <command, test, screenshot, manual check, or artifact that proves done>

## Open Questions

### Resolve Before Coding

- [ ] <question> - <why it blocks implementation>

### Deferred To Implementation

- [ ] <technical choice the agent can resolve while coding>

## Deferred Ideas

- <out-of-scope idea> - <why deferred>

## Handoff Note

CONTEXT.md is the source of truth. Decision IDs are stable. Implementation must
honor locked decisions, preserve listed patterns, and satisfy validation proof
before claiming done.
```
