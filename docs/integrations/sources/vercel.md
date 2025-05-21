# Vercel
 Vercel connector  enables seamless data sync between Vercel projects and various destinations. This integration simplifies real-time deployments, analytics, and automated workflows by bridging data from Vercel to your destination.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `access_token` | `string` | Access Token. Access token to authenticate with the Vercel API. Create and manage tokens in your Vercel account settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| user |  | DefaultPaginator | ✅ |  ❌  |
| deployments | uid | DefaultPaginator | ✅ |  ✅  |
| checks |  | DefaultPaginator | ✅ |  ❌  |
| environments |  | DefaultPaginator | ✅ |  ❌  |
| auth_tokens | id | DefaultPaginator | ✅ |  ❌  |
| aliases | uid | DefaultPaginator | ✅ |  ✅  |
| deployment_events | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.23 | 2025-05-10 | [59912](https://github.com/airbytehq/airbyte/pull/59912) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59564](https://github.com/airbytehq/airbyte/pull/59564) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58950](https://github.com/airbytehq/airbyte/pull/58950) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58553](https://github.com/airbytehq/airbyte/pull/58553) | Update dependencies |
| 0.0.19 | 2025-04-13 | [58036](https://github.com/airbytehq/airbyte/pull/58036) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57462](https://github.com/airbytehq/airbyte/pull/57462) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56867](https://github.com/airbytehq/airbyte/pull/56867) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56275](https://github.com/airbytehq/airbyte/pull/56275) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55616](https://github.com/airbytehq/airbyte/pull/55616) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55107](https://github.com/airbytehq/airbyte/pull/55107) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54460](https://github.com/airbytehq/airbyte/pull/54460) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54040](https://github.com/airbytehq/airbyte/pull/54040) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53518](https://github.com/airbytehq/airbyte/pull/53518) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53112](https://github.com/airbytehq/airbyte/pull/53112) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52398](https://github.com/airbytehq/airbyte/pull/52398) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51992](https://github.com/airbytehq/airbyte/pull/51992) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51441](https://github.com/airbytehq/airbyte/pull/51441) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50822](https://github.com/airbytehq/airbyte/pull/50822) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50373](https://github.com/airbytehq/airbyte/pull/50373) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49786](https://github.com/airbytehq/airbyte/pull/49786) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49421](https://github.com/airbytehq/airbyte/pull/49421) | Update dependencies |
| 0.0.2 | 2024-11-04 | [48270](https://github.com/airbytehq/airbyte/pull/48270) | Update dependencies |
| 0.0.1 | 2024-10-22 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
