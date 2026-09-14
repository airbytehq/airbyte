# legacy-task-load-parquet

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) connectors that use Parquet format only.

This toolkit contains Parquet format utilities for connectors that use the legacy task-based architecture. It provides Parquet schema generation, value conversion via Avro, and the `MapperPipeline` pattern that predates the modern dataflow pipeline.

## Do Not Use For New Connectors

New connectors should use `core-load` with the dataflow pipeline. For Iceberg/Parquet destinations, use `load-iceberg-parquet` instead. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-s3 (via legacy-task-load-object-storage)
- destination-azure-blob-storage (via legacy-task-load-object-storage)

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-parquet']
    useLegacyTaskLoader = true
}
```

## Contents

- Parquet writer utilities built on top of Avro
- `ParquetMapperPipelineFactory` - Legacy MapperPipeline for Parquet formatting
- Hadoop/Parquet configuration

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. For Iceberg-based destinations, use `load-iceberg-parquet`. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.