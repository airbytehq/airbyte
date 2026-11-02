# Contributing to source-postgres

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/platform/connector-development).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Xmin incremental checks reject wraparound** -- Xmin incremental sync is rejected when transaction-ID wraparound is detected, and the message directs users to CDC or a cursor-based mode.
2. **CTID partition state tracks table filenodes** -- A rewritten table causes the connector to restart its affected CTID read instead of trusting saved physical row positions.
3. **CDC replication slots advance during startup** -- CDC may advance its replication slot at startup based on saved progress; it does not make this advancement at checkpoints or sync completion.
4. **PostgreSQL-specific types have connector-defined encodings** -- Several PostgreSQL-specific types use non-obvious output formats that must remain consistent to avoid changing schemas or precision.

## Reproducing bugs

Use [source-postgres-e2e-tests](.agents/skills/source-postgres-e2e-tests/SKILL.md) for standard harness cases and [source-postgres-e2e-cdc-tests](.agents/skills/source-postgres-e2e-cdc-tests/SKILL.md) for CDC cases. The skills contain the supported invocations and setup details.
