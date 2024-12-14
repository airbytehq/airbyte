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
| 0.0.5 | 2024-12-14 | [49762](https://github.com/airbytehq/airbyte/pull/49762) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49392](https://github.com/airbytehq/airbyte/pull/49392) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48219](https://github.com/airbytehq/airbyte/pull/48219) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47595](https://github.com/airbytehq/airbyte/pull/47595) | Update dependencies |
| 0.0.1 | 2024-10-01 | | Initial release by [@avirajsingh7](https://github.com/avirajsingh7) via Connector Builder |

</details>
