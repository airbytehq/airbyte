# Testing A Custom Registry

## Purpose of this document
This document describes how to
1. Modify the connector catalog used by the platform
2. Use the newly modified catalog in the platform

## Why you might need to
1. You've added/updated/deleted a generally available connector and want to test it in the platform UI
1. You've added/updated/deleted a generally available connector and want to test it in the platform API

## Method 1: Edit the registry by hand (easiest)

### 1. Download the current OSS Registry
Download the current registry from [here](https://connectors.airbyte.com/files/registries/v0/oss_registry.json) to somewhere on your local machine.

### 2. Modify the registry
Modify the registry as you see fit. For example, you can add a new connector, update an existing connector, or delete a connector.

### 3. Upload the modified registry to a public location
Upload the modified registry to a public location. For example, you can upload it to a public S3 bucket, or you can upload it to a public GitHub repo, or a service like file.io

### 4. Point the platform to the modified registry
Run the platform with the following environment variable set:
```
REMOTE_CONNECTOR_CATALOG_URL = <url of the modified registry>
```

## Method 2: Use the registry generator (more involved)

Follow the steps in the [Metadata Orchestrator Readme](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/metadata_service/orchestrator/README.md)) to setup the orchestrator.

You can then use the public GCS url of the registry created by the orchestrator to point the platform to the modified registry.
```
REMOTE_CONNECTOR_CATALOG_URL = <url of the modified registry>
```