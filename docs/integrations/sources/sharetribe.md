# Sharetribe

This is the guide for the Sharetribe source connector which ingests data from the sharetribe integrations API.
Sharetribe is a no code marketplace builder tool. The important streams are `listings` and `transactions`.
Except for the `marketplace` endpoint, all the streams support incremental sync.

## Prerequisites

The source supports a number of API changes. For more information, checkout the website https://www.sharetribe.com/
This source uses the OAuth configuration for handling requests.

Once you create an account, log in and navigate to your sharetribe console.
In the sidebar, under the `Advanced` section, click on `Application` to create an application.
A client_ID and client_secret is required in order to setup a connection. Note down these credientials.
For more details about the API, check out https://www.sharetribe.com/api-reference/integration.html

## Set up the Adjust source connector

1. Click **Sources** and then click **+ New source**.
2. On the Set up the source page, select **Sharetribe** from the Source type dropdown.
3. Enter a name for your new source.
4. For **Client Id**, enter your client_id obtained in the previous step.
5. For **Client Secret**, enter your client_secret obtained in the previous step.
6. For **Start Date**, enter a start date from where you would like to sync the records.
7. Click **Set up source**.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | id | Default pagination | ✅ |   ✅ |
| marketplace | id | No pagination | ✅ |  ❌  |
| listings | id | Default pagination | ✅ |  ✅  |
| transactions | id | Default pagination | ✅ |  ✅  |
| events | id | Default pagination | ✅ |  ✅  |
| bookings | id | Default pagination | ✅ |  ✅  |
| messages | id | Default pagination | ✅ |  ✅  |
| reviews | id | Default pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.15 | 2025-03-09 | [55646](https://github.com/airbytehq/airbyte/pull/55646) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55125](https://github.com/airbytehq/airbyte/pull/55125) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54518](https://github.com/airbytehq/airbyte/pull/54518) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54051](https://github.com/airbytehq/airbyte/pull/54051) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53516](https://github.com/airbytehq/airbyte/pull/53516) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53023](https://github.com/airbytehq/airbyte/pull/53023) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52485](https://github.com/airbytehq/airbyte/pull/52485) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51884](https://github.com/airbytehq/airbyte/pull/51884) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51369](https://github.com/airbytehq/airbyte/pull/51369) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50728](https://github.com/airbytehq/airbyte/pull/50728) | Update dependencies |
| 0.0.5 | 2024-12-21 | [49709](https://github.com/airbytehq/airbyte/pull/49709) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49327](https://github.com/airbytehq/airbyte/pull/49327) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49055](https://github.com/airbytehq/airbyte/pull/49055) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48188](https://github.com/airbytehq/airbyte/pull/48188) | Update dependencies |
| 0.0.1 | 2024-10-03 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
