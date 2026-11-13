# Cloudflare Analytics
Connects to Cloudflare to retrieve some basic traffic analytics, including Core Web Vitals measurements.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Cloudflare token with Analytics Read access |  |
| `zone_id` | `string` | Zone ID. Your Cloudflare zone identifier |  |
| `start_date` | `string` | Start Date.  |  |
| `end_date` | `string` | End Date.  |  |
| `account_id` | `string` | Account ID. Your Cloudflare account identifier |  |
| `site_id` | `string` | Site Tag. The site tag used for Web Vitals tracking |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| daily_analytics | date | NoPagination | ✅ |  ✅  |
| browser_usage | date | NoPagination | ✅ |  ✅  |
| country_traffic | date | NoPagination | ✅ |  ✅  |
| response_status_codes | date | NoPagination | ✅ |  ✅  |
| core_web_vitals | date.requestPath.deviceType.userAgentBrowser.userAgentOS.countryName | NoPagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-07-13 | | Initial release by [@wouzzie](https://github.com/wouzzie) via Connector Builder |

</details>
