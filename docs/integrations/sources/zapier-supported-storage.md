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

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|:--------|:-----------|:---------------------------------------------------------| |
| 0.1.6 | 2024-06-21 | [39918](https://github.com/airbytehq/airbyte/pull/39918) | Update dependencies |
| 0.1.5 | 2024-06-04 | [39041](https://github.com/airbytehq/airbyte/pull/39041) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.4 | 2024-05-28 | [38728](https://github.com/airbytehq/airbyte/pull/38728) | Make connector compatible with builder |
| 0.1.3 | 2024-04-19 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37300](https://github.com/airbytehq/airbyte/pull/37300) | schema descriptions |
| 0.1.0 | 2022-10-25 | [18442](https://github.com/airbytehq/airbyte/pull/18442) | Initial release |

</details>
