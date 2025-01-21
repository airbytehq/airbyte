# Care Quality Commission
A manifest-only source for Care Quality Commission
https://www.cqc.org.uk/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your CQC Primary Key. See https://www.cqc.org.uk/about-us/transparency/using-cqc-data#api for steps to generate one. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| inspection_areas | inspectionAreaId | No pagination | ✅ |  ❌  |
| locations | locationId | DefaultPaginator | ✅ |  ❌  |
| providers | providerId | DefaultPaginator | ✅ |  ❌  |
| provider_locations | organisationId | No pagination | ✅ |  ❌  |
| locations_detailed | locationId | No pagination | ✅ |  ❌  |
| providers_detailed | providerId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                   |
|---------|------------|----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 0.0.11 | 2025-01-18 | [51777](https://github.com/airbytehq/airbyte/pull/51777) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51251](https://github.com/airbytehq/airbyte/pull/51251) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50495](https://github.com/airbytehq/airbyte/pull/50495) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50218](https://github.com/airbytehq/airbyte/pull/50218) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49546](https://github.com/airbytehq/airbyte/pull/49546) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49008](https://github.com/airbytehq/airbyte/pull/49008) | Update dependencies |
| 0.0.5 | 2024-11-05 | [48368](https://github.com/airbytehq/airbyte/pull/48368) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.4 | 2024-11-05 | [48329](https://github.com/airbytehq/airbyte/pull/48329) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47897](https://github.com/airbytehq/airbyte/pull/47897) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47671](https://github.com/airbytehq/airbyte/pull/47671) | Update dependencies |
| 0.0.1 | 2024-10-02 | [46315](https://github.com/airbytehq/airbyte/pull/46315) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
