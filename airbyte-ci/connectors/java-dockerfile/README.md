# Java Connector Dockerfile for Airbyte

This Dockerfile replicates the dagger-based build process for Java connectors used in Airbyte CI. It uses a multi-stage build approach to eliminate the need for Java to be installed locally.

## Features

- Multi-stage build process
- Builds the connector directly within the container
- Uses the same base image and scripts as the official Airbyte images
- Creates images that are compatible with the Airbyte platform

## Usage

### Building a connector image

Use the provided build script to build a connector image:

```bash
# Build the default connector (source-mysql)
./build.sh

# Build a specific connector
./build.sh --connector destination-postgres --tag latest
```

### Running the connector

```bash
# Run the connector spec command
docker run --rm airbyte/source-mysql:dev spec

# Run other commands
docker run --rm airbyte/source-mysql:dev check --config config.json
docker run --rm airbyte/source-mysql:dev discover --config config.json
docker run --rm airbyte/source-mysql:dev read --config config.json --catalog catalog.json
```

## Build Arguments

- `CONNECTOR_PATH`: Path to the connector directory (default: `airbyte-integrations/connectors/source-mysql`)
- `CONNECTOR_NAME`: Name of the connector (default: `source-mysql`)

## Environment Variables

The following environment variables are set in the image:

- `AIRBYTE_SPEC_CMD`: Command to run the spec operation
- `AIRBYTE_CHECK_CMD`: Command to run the check operation
- `AIRBYTE_DISCOVER_CMD`: Command to run the discover operation
- `AIRBYTE_READ_CMD`: Command to run the read operation
- `AIRBYTE_WRITE_CMD`: Command to run the write operation
- `AIRBYTE_ENTRYPOINT`: Path to the entrypoint script
- `APPLICATION`: Name of the connector
