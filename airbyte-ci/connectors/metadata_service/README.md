# Metadata Service
This is the begining of metadata service for airbyte.

This system is responsible for the following:
- Validating Connector metadata
- Storing Connector metadata in GCS
- Serving Connector metadata to various consumers
- Aggregating Connector metadata to provide a unified view of all connectors
- Triggering actions based on changes to Connector metadata

## Subsystems
- [Metadata Orchestrator](./orchestrator/README.md)