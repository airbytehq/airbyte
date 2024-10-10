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
| 0.0.1 | 2024-10-10 | [46707](https://github.com/airbytehq/airbyte/pull/46707) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
