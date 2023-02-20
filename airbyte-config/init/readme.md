# airbyte-config:init

This module fulfills two responsibilities:
1. It is where we declare what connectors should ship with the Platform. See below for more instruction on how it works.
2. It contains the scripts and Dockerfile that allow the `docker-compose` version of Airbyte to mount the local filesystem. This is helpful in cases where a user wants to use a connector that interacts with (reads data from or writes data to) the local filesystem. e.g. `destination-local-json`.

## Declaring connectors that ship with the Platform
In order to have a connector ship with the Platform it must be present in the respective `source_definitions.yaml` or `destination_definitions.yaml` files in `src/main/resources/seed`. If a connector is added there, the build system will handle fetching its spec and adding it to `source_specs.yaml` or `destination_specs.yaml`. See the gradle tasks to understand how this all works. The logic for fetching the specs is in `airbyte-config:specs`.
