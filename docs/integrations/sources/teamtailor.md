# Teamtailor
This is the setup for the Teamtailor source that ingests data from the teamtailor API.

Teamtailor is a recruitment software, provding a new way to attract and hire top talent https://www.teamtailor.com/

In order to use this source, you must first create an account on teamtailor.

Navigate to your organisation Settings Page -> API Key to create the required API token. You must also specify a version number and can use today's date as X-Api-Version to always get the latest version of the API.

Make sure to have the add-ons installed in your account for using the `nps-response` and `job-offers` endpoints.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `x_api_version` | `string` | X-Api-Version. The version of the API |  |
| `api` | `string` | api.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| candidates | id | DefaultPaginator | ✅ |  ❌  |
| custom-fields | id | DefaultPaginator | ✅ |  ❌  |
| departments | id | DefaultPaginator | ✅ |  ❌  |
| jobs | id | DefaultPaginator | ✅ |  ❌  |
| job-applications | id | DefaultPaginator | ✅ |  ❌  |
| job-offers | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| todos | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| team_memberships | id | DefaultPaginator | ✅ |  ❌  |
| stages | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| regions | id | DefaultPaginator | ✅ |  ❌  |
| referrals | id | DefaultPaginator | ✅ |  ❌  |
| questions | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| nps_responses | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-14 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
