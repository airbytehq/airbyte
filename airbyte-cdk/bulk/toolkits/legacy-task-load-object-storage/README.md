# legacy-task-load-object-storage

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) object storage connectors only.

This toolkit contains object storage loading infrastructure for connectors that use the legacy task-based architecture. It includes file formatting, upload/download utilities, and object storage operations that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New object storage connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-azure-blob-storage
- destination-s3
- destination-s3-data-lake
- destination-bigquery (indirectly via legacy-task-load-gcs)

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-object-storage']
    useLegacyTaskLoader = true
}
```

## Contents

- `ObjectLoaderPipeline` - Legacy pipeline for object storage operations
- File formatting utilities (CSV, Avro, Parquet)
- Object storage client abstractions

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.
