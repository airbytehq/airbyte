# DependancyTrack
The Dependency-Track Source Connector enables data extraction from Dependency-Track, an open-source platform for managing and analyzing software vulnerabilities across complex supply chains. Dependency-Track identifies and tracks vulnerabilities in project dependencies, enabling organizations to manage and reduce risk.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| project | uuid | DefaultPaginator | ✅ |  ❌  |
| search |  | DefaultPaginator | ✅ |  ❌  |
| team_self |  | DefaultPaginator | ✅ |  ❌  |
| vulnerability | vulnId | DefaultPaginator | ✅ |  ❌  |
| search_vulnerability |  | DefaultPaginator | ✅ |  ❌  |
| search_vulnerablesoftware |  | DefaultPaginator | ✅ |  ❌  |
| violation |  | DefaultPaginator | ✅ |  ❌  |
| cwe | cweId | DefaultPaginator | ✅ |  ❌  |
| finding_grouped_by_vulnerability | vulnerability | DefaultPaginator | ✅ |  ❌  |
| finding | component.vulnerability | DefaultPaginator | ✅ |  ❌  |
| licenses | licenseId | DefaultPaginator | ✅ |  ❌  |
| metrics_vulnerability |  | DefaultPaginator | ✅ |  ❌  |
| metrics_current_portfolio |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-11-19 | Initial release by [@Ameur94](https://github.com/Ameur94) via Connector Builder|

</details>