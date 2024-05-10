# Zapier Supported Storage

## Overview

The Zapier Supported Storage Connector can be used to sync your [Zapier](https://store.zapier.com/) data

#### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |
| `boolean`        | `boolean`    |       |

### Requirements

- secret - The Storage by Zapier secret.

## Changelog

| Version | Date | Pull Request | Subject |
|:--------|:-----------|:---------------------------------------------------------| |
| 0.1.3 | 2024-04-19 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | schema descriptions |
| 0.1.0 | 2022-10-25 | [18442](https://github.com/airbytehq/airbyte/pull/18442) | Initial release |
