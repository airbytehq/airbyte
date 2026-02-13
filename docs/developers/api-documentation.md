---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# API documentation

Use the Airbyte API to programmatically interact with Airbyte. You can extend it to:

- Control Airbyte in conjunction with orchestration tools like Airflow
- Use [Airbyte Embedded](https://airbyte.com/ai)

This article shows you how to get an access token and make your first request, and it provides strategies to manage token expiry.

## Get an access token

Before you can make requests to the API, you need an access token. For help with this, see [Get an access token](/platform/using-airbyte/configuring-api-access).

## Use the right base URL

The base URL to which you send API requests depends on whether you're using Airbyte Cloud or self-managing, and which domain you use to access the UI.

- **Airbyte Cloud**: `https://api.airbyte.com/v1/`

- **Self-managed**:

    - **Hosted locally**: `http://localhost:8000/api/public/v1/`

    - **Hosted on the web**: `<YOUR_AIRBYTE_URL>/api/public/v1/`

## Make your first API request

Send a GET request to list all the source connectors in your instance of Airbyte.

<Tabs>
<TabItem value="cloud" label="Cloud">

To send a request, insert your workspace ID and access token into the placeholder values below.

```bash title="Request"
curl --request GET \
     --url 'https://api.airbyte.com/v1/sources?workspaceIds=<YOUR_WORKSPACE_ID>' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

```json title="Response"
{
  "data": [
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Snowflake",
      "sourceType": "snowflake",
      "definitionId": "e2d65910-8c8b-40a1-ae7d-ee2416b2bfa2",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "host": "<YOUR_VALUE>",
        "role": "<YOUR_VALUE>",
        "cursor": {
          "cursor_method": "user_defined"
        },
        "database": "<YOUR_VALUE>",
        "warehouse": "<YOUR_VALUE>",
        "concurrency": 1,
        "credentials": {
          "password": "************",
          "username": "<YOUR_USER>",
          "auth_type": "username/password"
        },
        "check_privileges": true,
        "checkpoint_target_interval_seconds": 300
      },
      "createdAt": 1758053604
    },
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Stripe",
      "sourceType": "stripe",
      "definitionId": "e094cb9a-26de-4645-8761-65c0c425d1de",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "account_id": "<YOUR_ACCOUNT_ID>",
        "start_date": "2023-07-01T00:00:00Z",
        "num_workers": 10,
        "slice_range": 365,
        "client_secret": "************",
        "lookback_window_days": 0
      },
      "createdAt": 1755562809
    }
  ],
  "previous": "",
  "next": ""
}
```

</TabItem>
<TabItem value="sm-local" label="Self-managed (localhost)">

To send a request, insert your access token into the placeholder value below.

```bash title="Request"
curl --request GET \
     --url 'http://localhost:8000/api/public/v1/sources' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

```json title="Response"
{
  "data": [
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Snowflake",
      "sourceType": "snowflake",
      "definitionId": "e2d65910-8c8b-40a1-ae7d-ee2416b2bfa2",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "host": "<YOUR_VALUE>",
        "role": "<YOUR_VALUE>",
        "cursor": {
          "cursor_method": "user_defined"
        },
        "database": "<YOUR_VALUE>",
        "warehouse": "<YOUR_VALUE>",
        "concurrency": 1,
        "credentials": {
          "password": "************",
          "username": "<YOUR_USER>",
          "auth_type": "username/password"
        },
        "check_privileges": true,
        "checkpoint_target_interval_seconds": 300
      },
      "createdAt": 1758053604
    },
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Stripe",
      "sourceType": "stripe",
      "definitionId": "e094cb9a-26de-4645-8761-65c0c425d1de",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "account_id": "<YOUR_ACCOUNT_ID>",
        "start_date": "2023-07-01T00:00:00Z",
        "num_workers": 10,
        "slice_range": 365,
        "client_secret": "************",
        "lookback_window_days": 0
      },
      "createdAt": 1755562809
    }
  ],
  "previous": "",
  "next": ""
}
```

</TabItem>
<TabItem value="sm-web" label="Self-managed">

To send a request, insert your access token into the placeholder value below.

```bash title="Request"
curl --request GET \
     --url '<YOUR_AIRBYTE_URL>/api/public/v1/sources' \
     --header 'accept: application/json' \
     --header 'authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

```json title="Response"
{
  "data": [
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Snowflake",
      "sourceType": "snowflake",
      "definitionId": "e2d65910-8c8b-40a1-ae7d-ee2416b2bfa2",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "host": "<YOUR_VALUE>",
        "role": "<YOUR_VALUE>",
        "cursor": {
          "cursor_method": "user_defined"
        },
        "database": "<YOUR_VALUE>",
        "warehouse": "<YOUR_VALUE>",
        "concurrency": 1,
        "credentials": {
          "password": "************",
          "username": "<YOUR_USER>",
          "auth_type": "username/password"
        },
        "check_privileges": true,
        "checkpoint_target_interval_seconds": 300
      },
      "createdAt": 1758053604
    },
    {
      "sourceId": "<YOUR_SOURCE_ID>",
      "name": "Stripe",
      "sourceType": "stripe",
      "definitionId": "e094cb9a-26de-4645-8761-65c0c425d1de",
      "workspaceId": "<YOUR_WORKSPACE_ID>",
      "configuration": {
        "account_id": "<YOUR_ACCOUNT_ID>",
        "start_date": "2023-07-01T00:00:00Z",
        "num_workers": 10,
        "slice_range": 365,
        "client_secret": "************",
        "lookback_window_days": 0
      },
      "createdAt": 1755562809
    }
  ],
  "previous": "",
  "next": ""
}
```

</TabItem>
</Tabs>

## Handle access token expiry in your requests

Access tokens are short-lived and you need to regularly request a new one. To minimize unnecessary requests and authorization errors, ensure your API requests work together with requests for new access tokens.

- When you get a new access token, cache it with the expected expiry time.

- Validate that your access token isn't expired before making a request. If it's expired, get a new access token before proceeding with the request.

- If you receive a `401 Unauthorized` response, request a new access token and try the request again one time. Don't keep making requests if you receive consecutive 401 responses.

## Full reference documentation

Find Airbyte's full API documentation at [reference.airbyte.com](https://reference.airbyte.com/reference/getting-started).

## Configuration API

Airbyte has deprecated the configuration API and no longer supports it. The Configuration API is an internal API designed for communication between different Airbyte components, not for managing an Airbyte deployment.

Use the Configuration API at your own risk. Airbyte engineers may modify it without warning.
