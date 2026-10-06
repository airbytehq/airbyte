# legacy-task-load-db

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) database connectors only.

This toolkit contains database-specific loading infrastructure for connectors that use the legacy task-based architecture. It includes typing/deduping utilities, SQL generation, and table operations that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New database connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-bigquery
- destination-mssql

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-db']
    useLegacyTaskLoader = true
}
```

## Contents

- `legacy_typing_deduping/` - Typing and deduping table operations
- `direct_load_table/` - Direct load table operations
- Database handler interfaces and SQL generation utilities

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.