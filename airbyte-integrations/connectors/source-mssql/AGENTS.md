> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-mssql: Unique Connector Behaviors

## 1. "Exclude Today's Data" uses UTC day cutoffs

For supported temporal cursor types, the "Exclude Today's Data" option calculates the start of the current UTC day and uses a strict `< cutoff` predicate for both cursor-bound discovery and record reads.

**Why this matters:** This is a day-level exclusion rather than a moving timestamp window. Changing the timezone or predicate can include current-day rows or omit rows from earlier days.

## 2. Cursor-incremental partitions omit the upper bound for datetime2(7)

Resumable cursor-incremental partitions use a lower bound without a `MAX(cursor)` upper-bound ceiling. MSSQL `datetime2(7)` values have seven fractional digits, while cursor values can be truncated to six; a ceiling at the truncated maximum could exclude rows whose seventh digit is greater.

**Why this matters:** Reintroducing an upper bound can silently skip rows at a partition boundary. Preserve the open-ended partition behavior unless cursor precision and the query comparison are changed together.

## 3. Null legacy cursor state resets to a cold start

When migrated stream state has a cursor field but a null cursor value, the partition factory resets that stream and starts it cold rather than binding SQL `NULL` as the cursor position.

**Why this matters:** A null legacy value is not a valid resume point. Treating it as one can generate incorrect predicates or make the stream appear resumable when it is not.

## 4. CDC starts at current max LSN and validates capture instances

A cold CDC start reads `sys.fn_cdc_get_max_lsn()` as its starting point. For warm state, the connector validates the saved LSN against the selected streams' accessible capture instances; missing CDC access is a configuration error, not an invalid-history condition eligible for state reset.

**Why this matters:** The cold-start position and capture-instance checks define whether CDC can safely resume. Do not conflate missing permissions or capture instances with an expired LSN and automatically reset state.

## Reproducing bugs and testing

See [CONTRIBUTING.md](CONTRIBUTING.md#reproducing-bugs-locally) for the merged local harness, troubleshooting, and comparison-mode guidance. The harness skills are
[source-mssql-e2e-tests](.agents/skills/source-mssql-e2e-tests/SKILL.md) and
[source-mssql-e2e-cdc-tests](.agents/skills/source-mssql-e2e-cdc-tests/SKILL.md).
