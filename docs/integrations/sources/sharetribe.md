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
| 0.0.1 | 2024-10-03 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
