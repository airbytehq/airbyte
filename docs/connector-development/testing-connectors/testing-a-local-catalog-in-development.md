# Testing The Local Catalog

## Purpose of this document
This document describes how to
1. Generate the OSS catalog in the `airbyte` repo
1. Move the OSS catalog to the `airbyte-platform` repo
1. Point the platform to the new catalog
1. Run the platform

## Why you might need to
1. You've added/updated/deleted a generally available connector and want to test it in the platform UI
1. You've added/updated/deleted a generally available connector and want to test it in the platform API

## Steps

### 1. Generate the OSS Catalog
In the `airbyte` repo run
```sh
SUB_BUILD=ALL_CONNECTORS ./gradlew :airbyte-config:specs:generateOssConnectorCatalog
```

### 2. Move the OSS catalog to platform
In the `airbyte` repo run
```sh
cp airbyte-config/init/src/main/resources/seed/oss_catalog.json <PATH_TO_PLATFORM_REPO>/airbyte-config/init/src/main/resources/seed/local_dev_catalog.json
```

### 3. Point the platform to the new catalog
In the `airbyte-platform` repo modify `.env` add the environment variable
```sh
LOCAL_CONNECTOR_CATALOG_PATH=seed/local_dev_catalog.json
```

### 4. Build the platform
In the `airbyte-platform` run
```sh
SUB_BUILD=PLATFORM ./gradlew build -x test
```

### 4. Run platform
In the `airbyte-platform` run
```sh
VERSION=dev docker-compose up
```

Success! Your new catalog should now be loaded into the database.
