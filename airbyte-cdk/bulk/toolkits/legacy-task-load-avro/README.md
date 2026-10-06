# legacy-task-load-avro

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) connectors that use Avro format only.

This toolkit contains Avro format utilities for connectors that use the legacy task-based architecture. It provides Avro schema generation, value conversion, and the `MapperPipeline` pattern that predates the modern dataflow pipeline.

## Do Not Use For New Connectors

New connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-s3
- destination-azure-blob-storage (via legacy-task-load-object-storage)

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-avro']
    useLegacyTaskLoader = true
}
```

## Contents

- `AirbyteTypeToAvroSchema` - Convert Airbyte types to Avro schema
- `AirbyteValueToAvroRecord` - Convert Airbyte values to Avro records
- `AvroMapperPipelineFactory` - Legacy MapperPipeline for Avro formatting

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.