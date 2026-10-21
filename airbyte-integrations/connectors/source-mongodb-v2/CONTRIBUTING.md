# Contributing to source-mongodb-v2

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/platform/connector-development).

## Unique behaviors (summary)

Full technical detail for each item lives in [AGENTS.md](./AGENTS.md).

1. **Schemaless mode packs fields into `data`** -- Schemaless streams always have the same schema: `_id`, a `data` object holding the document, and the CDC metadata columns. Schema-enforced mode exposes each sampled document field as a top-level property.
2. **Schema-enforced discovery samples a configurable number of documents** -- MongoDB has no fixed schema, so schema-enforced discovery infers field names and types from a document sample. Fields that don't appear in the sample can be missing from the catalog.
3. **Invalid resume tokens fail or reset according to configuration** -- Invalid saved resume tokens fail by default, with a configurable full-refresh option.
4. **Update capture defaults to Lookup** -- Post-image capture requires MongoDB's matching change-stream configuration, or update data can be lost.

`source-mongodb-v2` is a Java connector on the legacy Java CDK. Standard local
commands:

```bash
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:test
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:assemble
./gradlew :airbyte-integrations:connectors:source-mongodb-v2:dockerBuildx
```

## Reproducing bugs locally

Use the
[`source-mongodb-v2-e2e-tests`](.agents/skills/source-mongodb-v2-e2e-tests/SKILL.md)
skill for non-CDC local sweeps. It stands up a single-node MongoDB 7.0
replica set (`source-mongodb-v2-db-backend`), applies `mongosh` JavaScript
fixtures (MongoDB has no SQL; the engine's `apply-sql.sh` entrypoint takes a
`.js` file), and sweeps `spec` → `check` → `discover` → `read` against
`airbyte/source-mongodb-v2:<tag>`. Orchestration is delegated to
[`airbyte-integrations/db-harness-lib/`](../../db-harness-lib/).

There is no `source-mongodb-v2-e2e-cdc-tests` skill yet: change-stream
(CDC) replay with resume tokens is not covered by the local harness. If the
reported failure is CDC-mode, say so in the evidence plan rather than
forcing the generic skill to cover it.

```bash
cd airbyte-integrations/connectors/source-mongodb-v2

# Single-version sweep
poe e2e-local --test-version=<tag>

# Prove-fix comparison (target vs. known-bad control)
poe e2e-local --test-version=<tag> --control-version=<control-tag>
```

**Never** repro against a customer connection, Atlas cluster, or Airbyte
Cloud instance.
