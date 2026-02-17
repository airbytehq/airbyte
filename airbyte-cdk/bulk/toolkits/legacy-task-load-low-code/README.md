# legacy-task-load-low-code

> **DEPRECATED**: This toolkit is for legacy (non-dataflow) low-code destination connectors only.

This toolkit contains low-code destination infrastructure for connectors that use the legacy task-based architecture. It provides YAML configuration parsing, Jinja templating, and HTTP request utilities that predate the modern dataflow pipeline.

## Do Not Use For New Connectors

New low-code connectors should use `core-load` with the dataflow pipeline. This toolkit should only be used and updated for the existing connectors that depend on it.

## Connectors Using This Toolkit

- destination-customer-io
- destination-hubspot

## Configuration

To use this toolkit, add it to your connector's toolkits list along with `useLegacyTaskLoader`:

```groovy
airbyteBulkConnector {
    core = 'load'
    toolkits = ['legacy-task-load-low-code']
    useLegacyTaskLoader = true
}
```

## Contents

- YAML configuration parsing
- Jinja templating support
- HTTP request utilities
- Dead Letter Queue (DLQ) integration

## Migration Path

Connectors should migrate to the modern dataflow pipeline when possible. The dataflow architecture provides better performance, cleaner separation of concerns, and is the actively maintained code path.