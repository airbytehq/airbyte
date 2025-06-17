# Yotpo

This page contains the setup guide and reference information for the [Yotpo](https://apidocs.yotpo.com/reference/welcome) source connector.

## Prerequisites

To set up the Yotpo source connector, you need:

1. A Yotpo account with API access
2. Your Yotpo App Key (found in your Yotpo account settings)
3. An Access Token generated from the Yotpo API

## Setup guide

### Step 1: Generate an Access Token

1. You need your App Key and API Secret to generate an access token
2. Find your App Key and API Secret in your [Yotpo account settings](https://settings.yotpo.com/#/general_settings)
3. Generate an access token using the [Yotpo authentication endpoint](https://apidocs.yotpo.com/reference/yotpo-authentication):
   ```
   POST https://api.yotpo.com/oauth/token
   ```
   with the following parameters:
   ```json
   {
     "client_id": "YOUR_APP_KEY",
     "client_secret": "YOUR_API_SECRET",
     "grant_type": "client_credentials"
   }
   ```
4. Store the returned access token securely as it will be used for all API calls

### Step 2: Set up the Yotpo connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account
2. In the left navigation bar, click **Sources**. In the top-right corner, click **New Source**
3. On the Set up the source page, enter the name for the Yotpo connector and select **Yotpo** from the Source type dropdown
4. Enter the following required parameters:
   - `access_token`: The access token generated in Step 1
   - `app_key`: Your Yotpo App Key
   - `start_date`: The date from which you want to start syncing data (format: YYYY-MM-DDT00:00:00.000Z)
   - `email`: Your registered email address with Yotpo
5. Click **Set up source**

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Enter the required parameters as described above
4. Click **Set up source**

## Supported sync modes

The Yotpo source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

| Stream Name      | Description                                                  | Incremental | Notes |
|------------------|--------------------------------------------------------------|-------------|-------|
| email_analytics  | Retrieves aggregated data for email metrics                  | No          | Data is grouped by metrics and can be filtered by date range |
| raw_data         | Returns detailed data about every email sent from Yotpo      | No          | Includes email recipient, delivery status, open/click events |
| reviews          | Retrieves product reviews                                    | Yes         | Uses `created_at` as cursor field with a lookback window of 31 days |
| unsubscribers    | Lists users who have unsubscribed from emails                | No          | Limited to 5000 responses per request, requires pagination for larger datasets |
| webhooks         | Lists all webhooks created for the account                   | No          | Includes webhook URL and event type information |
| webhook_events   | Lists available webhook event types                          | No          | Includes event names and descriptions |

## Performance considerations

### Rate Limits

- The Reviews endpoint is limited to 5,000 requests per minute per app key
- For Reviews, it's recommended to query up to 100 reviews per request (default is 10)
- Review data is retrieved with a delay of 1 hour

### Pagination

- For the Reviews stream, pagination is handled automatically using page and count parameters
- For the Unsubscribers stream, if your list exceeds 5000 email addresses, you must use the count and page parameters for pagination

## API method example

```
GET https://api.yotpo.com/v1/apps/{app_key}/reviews?utoken={access_token}
```

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                            | Subject        |
| :------ | :--------- | :------------------------------------------------------ | :------------- |
| 0.2.1 | 2025-06-15 | [47597](https://github.com/airbytehq/airbyte/pull/47597) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44780](https://github.com/airbytehq/airbyte/pull/44780) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-24 | [44661](https://github.com/airbytehq/airbyte/pull/44661) | Update dependencies |
| 0.1.13 | 2024-08-17 | [44254](https://github.com/airbytehq/airbyte/pull/44254) | Update dependencies |
| 0.1.12 | 2024-08-12 | [43891](https://github.com/airbytehq/airbyte/pull/43891) | Update dependencies |
| 0.1.11 | 2024-08-10 | [43658](https://github.com/airbytehq/airbyte/pull/43658) | Update dependencies |
| 0.1.10 | 2024-08-03 | [43198](https://github.com/airbytehq/airbyte/pull/43198) | Update dependencies |
| 0.1.9 | 2024-07-27 | [42610](https://github.com/airbytehq/airbyte/pull/42610) | Update dependencies |
| 0.1.8 | 2024-07-20 | [42275](https://github.com/airbytehq/airbyte/pull/42275) | Update dependencies |
| 0.1.7 | 2024-07-13 | [41815](https://github.com/airbytehq/airbyte/pull/41815) | Update dependencies |
| 0.1.6 | 2024-07-10 | [41444](https://github.com/airbytehq/airbyte/pull/41444) | Update dependencies |
| 0.1.5 | 2024-07-09 | [41250](https://github.com/airbytehq/airbyte/pull/41250) | Update dependencies |
| 0.1.4 | 2024-07-06 | [40795](https://github.com/airbytehq/airbyte/pull/40795) | Update dependencies |
| 0.1.3 | 2024-06-25 | [40488](https://github.com/airbytehq/airbyte/pull/40488) | Update dependencies |
| 0.1.2 | 2024-06-21 | [39945](https://github.com/airbytehq/airbyte/pull/39945) | Update dependencies |
| 0.1.1 | 2024-05-20 | [38390](https://github.com/airbytehq/airbyte/pull/38390) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2023-04-14 | [Init](https://github.com/airbytehq/airbyte/pull/25532) | Initial commit |

</details>
