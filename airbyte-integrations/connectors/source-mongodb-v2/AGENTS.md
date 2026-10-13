> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-mongodb-v2: Unique Connector Behaviors

## 1. Schemaless mode packs fields into `data`

With `schema_enforced` disabled, the catalog replaces individual document fields with a packed object field named `data`. Schema-enforced mode instead exposes discovered document fields as stream properties.

**Why this matters:** These modes produce different record shapes and schemas. Code that reads or transforms source fields must not assume that fields are top-level in schemaless mode.

## 2. Schema-enforced discovery samples a configurable number of documents

Schema-enforced discovery samples `discover_sample_size` documents to infer each collection's fields; the default is 10,000. Fields absent from the sample may not appear in the discovered schema. Schemaless mode uses a one-document sample to inspect `_id` information, not the schema-enforced sample size.

**Why this matters:** Discovery is sample-based, not a complete inventory of all fields in a collection. Changes to the sampling pipeline or defaults can alter schema coverage and should preserve the distinct schemaless behavior.

## 3. Invalid resume tokens fail or reset according to configuration

When a saved CDC resume token is invalid, `invalid_cdc_cursor_position_behavior` controls whether the connector fails or resets state for a full refresh. The default behavior is `Fail sync`; `Re-sync data` triggers the refresh.

**Why this matters:** A full refresh after token expiry can be expensive, while continuing from an invalid token is not possible. Keep the explicit fail-versus-refresh choice and its default intact.

## 4. Update capture defaults to Lookup

The default update capture mode is `Lookup`; selecting `Post Image` configures Debezium to use post-images. The spec warns that MongoDB must have the required pre/post-image settings enabled or data loss can occur.

**Why this matters:** The mode depends on server-side change-stream configuration and affects the document content emitted for updates. Changing the default or Debezium property without preserving the server requirements can lose update data.

## Reproducing bugs and testing

See [CONTRIBUTING.md](CONTRIBUTING.md#reproducing-bugs-locally) and the
[source-mongodb-v2-e2e-tests](.agents/skills/source-mongodb-v2-e2e-tests/SKILL.md)
skill for the available non-CDC local harness. CDC replay with resume tokens is not covered by that harness.
