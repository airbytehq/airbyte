# Metadata Service

Airbyte Metadata Service manages the Airbyte Connector Registry.

This system is responsible for the following:

- Validating Connector metadata
- Storing Connector metadata in GCS
- Serving Connector metadata to various consumers
- Aggregating Connector metadata to provide a unified view of all connectors
- Triggering actions based on changes to Connector metadata

## Subsystems

- [Metadata Lib](./lib) responsible for preparing and validating connector metadata.
- [Metadata Orchestrator](./orchestrator) responsible for gathering metadata into the registry,
  using Dagster.
