# Solarwinds Service Desk
## Overview

The Solarwinds Service Desk connector support both Full sync and Incremental.

Documentation: https://apidoc.samanage.com/#section/General-Concepts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key. Refer to `https://documentation.solarwinds.com/en/success_center/swsd/content/completeguidetoswsd/token-authentication-for-api-integration.htm#link4` |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| hardwares | id | DefaultPaginator | ✅ |  ✅  |
| risks | id | DefaultPaginator | ✅ |  ✅  |
| audits | uuid | DefaultPaginator | ✅ |  ✅  |
| vendors | id | DefaultPaginator | ✅ |  ❌  |
| purchase_orders | id | DefaultPaginator | ✅ |  ✅  |
| contracts | id | DefaultPaginator | ✅ |  ✅  |
| assets | id | DefaultPaginator | ✅ |  ✅  |
| mobiles | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| departments | id | DefaultPaginator | ✅ |  ❌  |
| sites | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| configuration_items | id | DefaultPaginator | ✅ |  ✅  |
| solutions | id | DefaultPaginator | ✅ |  ✅  |
| releases | id | DefaultPaginator | ✅ |  ✅  |
| change_catalogs | id | DefaultPaginator | ✅ |  ✅  |
| changes | id | DefaultPaginator | ✅ |  ✅  |
| incidents | id | DefaultPaginator | ✅ |  ✅  |
| catalog_items | id | DefaultPaginator | ✅ |  ✅  |
| problems | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-11 | [51409](https://github.com/airbytehq/airbyte/pull/51409) | Update dependencies |
| 0.0.7 | 2025-01-04 | [50748](https://github.com/airbytehq/airbyte/pull/50748) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50360](https://github.com/airbytehq/airbyte/pull/50360) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49771](https://github.com/airbytehq/airbyte/pull/49771) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49418](https://github.com/airbytehq/airbyte/pull/49418) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49111](https://github.com/airbytehq/airbyte/pull/49111) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-29 | [47855](https://github.com/airbytehq/airbyte/pull/47855) | Update dependencies |
| 0.0.1 | 2024-10-10 | [46707](https://github.com/airbytehq/airbyte/pull/46707) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
