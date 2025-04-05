# People Data Labs
Website: https://dashboard.peopledatalabs.com/
API Reference: https://docs.peopledatalabs.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the People Data Labs API. You can find or generate your API key in your People Data Labs account dashboard at https://peopledatalabs.com/signup/. |  |
| `start_date` | `string` | Start date.  |  |
| `name_filter` | `string` | Name filter for search. Name filter for searching streams | Rick Morty |
| `email_filter` | `string` | Email filter for search. Email filter for search endpoints | test@gmail.com |
| `company_name_filter` | `string` | Company name filter. Company Name for search streams | Google |
| `location_name_filter` | `string` | Location name filter. The location name filter for search streams | boston |
| `ip_addr` | `string` | IP Address. IP address for enrich stream | 76.155.190.200 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| person_enrich | id | No pagination | ✅ |  ✅  |
| person_identify | uuid | No pagination | ✅ |  ❌  |
| company_clean | id | No pagination | ✅ |  ❌  |
| location_clean | uuid | No pagination | ✅ |  ❌  |
| company_enrich | uuid | No pagination | ✅ |  ❌  |
| ip_enrich | uuid | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-05 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
