# airbyte-config:init

This module fulfills two responsibilities:
1. It is where we declare what connectors should ship with the Platform. See below for more instruction on how it works.
2. It contains the scripts and Dockerfile that allow the `docker-compose` version of Airbyte to mount the local filesystem. This is helpful in cases where a user wants to use a connector that interacts with (reads data from or writes data to) the local filesystem. e.g. `destination-local-json`.

## The Connector Registry and Spec Secret Masks
The connector registry (list of available connectors) is downloaded at runtime from https://connectors.airbyte.com/files/registries/v0/oss_registry.json

The spec secret mask (one of the multiple systems that hide your secrets from the logs) is also downloaded at runtime from https://connectors.airbyte.com/files/registries/v0/spec_secret_mask.json

The logic inside the folder is responsible for downloading these files and making them available to the platform.