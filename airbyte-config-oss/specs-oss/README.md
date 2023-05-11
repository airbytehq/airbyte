# The Connector Registry and Spec Secret Masks
The connector registry (list of available connectors) is downloaded at runtime from https://connectors.airbyte.com/files/registries/v0/oss_registry.json

The spec secret mask (one of the multiple systems that hide your secrets from the logs) is also downloaded at runtime from https://connectors.airbyte.com/files/registries/v0/spec_secret_mask.json

The logic inside the folder is responsible for downloading these files and making them available to the platform.