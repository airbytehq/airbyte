# legacy-task-load-s3

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) S3 connectors only.

This toolkit contains S3-specific loading infrastructure for connectors that use the legacy task-based architecture. It provides S3 client wrappers and upload utilities that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New S3 connectors should use `core-load` with the dataflow pipeline, using `load-aws` for AWS credentials only. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-s3
- destination-s3-data-lake
- destination-bigquery

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-s3']
    useLegacyTaskLoader = true
}
```

## Contents

- S3 client wrappers (both AWS SDK v1 and v2)
- S3 upload/download utilities
- S3-specific configuration handling

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. For AWS credentials, use `load-aws` instead. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.