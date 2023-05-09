# airbyte-config:init

This module fulfills two responsibilities:
1. It is where we declare what connectors should ship with the Platform. See below for more instruction on how it works.
2. It contains the scripts and Dockerfile that allow the `docker-compose` version of Airbyte to mount the local filesystem. This is helpful in cases where a user wants to use a connector that interacts with (reads data from or writes data to) the local filesystem. e.g. `destination-local-json`.

## Declaring connectors that ship with the Platform
In order to have a connector ship with the Platform it must have a `metadata.yaml` file in its folder with `data.registries.oss` set to `true`. This file contains metadata about the connector such as its name, description, and whether it is a source or destination. This file is used to generate the `oss_catalog.json` file that is used by the Platform to populate the list of connectors that ship with the Platform.