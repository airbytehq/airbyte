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
| 0.0.1   | 2024-10-02 | [46315](https://github.com/airbytehq/airbyte/pull/46315) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
