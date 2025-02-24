# Xsolla
The Xsolla Airbyte Connector enables seamless integration between Xsolla and various data destinations. This connector allows you to extract data from Xsolla’s APIs, such as Game Catalog, Virtual Items, Virtual Currency and more.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Go to Xsolla Dashboard and from company setting get the api_key |  |
| `project_id` | `number` | Project Id. You can find this parameter in your Publisher Account next to the name of the project . Example: 44056 |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Games Catalog | item_id | DefaultPaginator | ✅ |  ❌  |
| DRM | drm_id | No pagination | ✅ |  ❌  |
| Virtual Items | item_id | DefaultPaginator | ✅ |  ❌  |
| Virtual Currency | item_id | DefaultPaginator | ✅ |  ❌  |
| Virtual Currency Package | item_id | DefaultPaginator | ✅ |  ❌  |
| Bundles | item_id | DefaultPaginator | ✅ |  ❌  |
| Reward Chains | reward_chain_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.14 | 2025-02-22 | [54489](https://github.com/airbytehq/airbyte/pull/54489) | Update dependencies |
| 0.0.13 | 2025-02-15 | [54066](https://github.com/airbytehq/airbyte/pull/54066) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53529](https://github.com/airbytehq/airbyte/pull/53529) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53071](https://github.com/airbytehq/airbyte/pull/53071) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52457](https://github.com/airbytehq/airbyte/pull/52457) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51970](https://github.com/airbytehq/airbyte/pull/51970) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51392](https://github.com/airbytehq/airbyte/pull/51392) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50813](https://github.com/airbytehq/airbyte/pull/50813) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50350](https://github.com/airbytehq/airbyte/pull/50350) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49762](https://github.com/airbytehq/airbyte/pull/49762) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49392](https://github.com/airbytehq/airbyte/pull/49392) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48219](https://github.com/airbytehq/airbyte/pull/48219) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47595](https://github.com/airbytehq/airbyte/pull/47595) | Update dependencies |
| 0.0.1 | 2024-10-01 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
