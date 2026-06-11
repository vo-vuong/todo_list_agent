# Decision Probes

Use these probes to find the next highest-leverage question. Choose only probes that are unstated, user-facing, and likely to change implementation.

## SEE

- Layout: list, table, card grid, timeline, canvas, form, modal, or another pattern?
- Density: compact power-user view or spacious casual view?
- Responsive behavior: same layout, stacked layout, hidden columns, or separate mobile flow?
- States: empty, loading, error, hover, focus, selected, disabled.
- Interaction: read-only, inline edit, explicit save, drag, destructive confirmation.
- Lists: pagination, load more, infinite scroll, sorting, filtering, truncation.

## CALL

- Input shape: params, body, flags, payload, SDK object, or stream?
- Success shape: full resource, ID, status, stream, async job handle, or no content?
- Caller and auth: internal, user session, API key, JWT, OAuth, anonymous?
- Errors: status/code format, structured details, retry signal, rate-limit signal.
- Behavior: idempotent, retryable, dry-run, side effects, timeout expectations.

## RUN

- Trigger: cron, event, message, command, webhook, or manual run?
- Concurrency: single instance, bounded pool, parallel allowed, lock needed?
- Output: stdout, log, database row, notification, report, artifact?
- Progress: none, counts, percentage, verbose mode?
- Failure: abort, continue with logged failures, retry/backoff, notify, archive?
- Modes: dry-run, force, resource limits?

## READ

- Structure: narrative, step-by-step, reference table, anchors, multi-page?
- Audience: beginner, intermediate, expert, operator, customer?
- Tone and depth: conversational, formal, terse reference, explain-from-scratch?
- Required sections, examples, callouts, warnings, versioning, maintenance cadence?

## ORGANIZE

- Grouping: type, domain, date, owner, status, priority?
- Nesting depth and membership rules?
- Naming: casing, prefixes, suffixes, stability, conflict resolution?
- Exceptions: ungrouped items, orphan handling, multi-group items?
- Evolution: migration needed, stable from day one, approval process for new groups?

## Cross-Cutting

- What is explicitly out of scope?
- Which adjacent feature is touched but not owned?
- What existing pattern should this follow or intentionally diverge from?
- Who or what consumes the output?
- Does the output need to be human-readable, machine-readable, or both?
- What proof should exist before claiming the work is done?
