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
| 0.0.6 | 2024-12-14 | [49742](https://github.com/airbytehq/airbyte/pull/49742) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49439](https://github.com/airbytehq/airbyte/pull/49439) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49122](https://github.com/airbytehq/airbyte/pull/49122) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [47909](https://github.com/airbytehq/airbyte/pull/47909) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47540](https://github.com/airbytehq/airbyte/pull/47540) | Update dependencies |
| 0.0.1 | 2024-10-14 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
