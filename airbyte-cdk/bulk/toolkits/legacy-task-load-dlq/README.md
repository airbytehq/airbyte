# legacy-task-load-dlq

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) connectors with Dead Letter Queue support only.

This toolkit contains Dead Letter Queue (DLQ) infrastructure for connectors that use the legacy task-based architecture. It provides error handling and DLQ upload utilities that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- Used by low-code destination connectors (via load-low-code)

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-dlq']
    useLegacyTaskLoader = true
}
```

## Contents

- DLQ error handling utilities
- DLQ upload infrastructure
- Error record storage

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.