# legacy-task-load-azure-blob-storage

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) Azure Blob Storage connectors only.

This toolkit contains Azure Blob Storage-specific loading infrastructure for connectors that use the legacy task-based architecture. It provides Azure client wrappers and upload utilities that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New Azure connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-azure-blob-storage

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-azure-blob-storage']
    useLegacyTaskLoader = true
}
```

## Contents

- Azure Blob Storage client wrappers
- Azure upload/download utilities
- Azure-specific configuration handling

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.