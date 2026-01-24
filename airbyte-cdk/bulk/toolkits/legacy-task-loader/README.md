# legacy-task-loader

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) connectors only.

This toolkit contains the pre-dataflow task-based loading infrastructure from CDK version 0.1.73. It exists to support existing connectors that have not yet migrated to the modern dataflow pipeline architecture.

## Do Not Use For New Connectors

New connectors should use `core-load` and the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-bigquery
- destination-azure-blob-storage
- destination-s3
- destination-mssql
- destination-customer-io
- destination-hubspot
- destination-s3-data-lake

## Configuration

To use this toolkit, add `useLegacyTaskLoader = true` in your connector's build.gradle:

```groovy
airbyteBulkConnector {
    core = 'load'
    useLegacyTaskLoader = true
}
```

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.