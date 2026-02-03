# Infor Nexus Datasets

The Infor Nexus Datasets source connector syncs data from the Infor Nexus Data Mesh API. This connector allows you to extract datasets that have been configured for export in your Infor Nexus organization.

For more information, see the [Infor Nexus Developer Network](https://developer.infornexus.com/).

## Prerequisites

- Nexus customer organization with Data Mesh rights
- Export data set created in the customer organization
- Data API Agent user configured in the customer organization

## Airbyte OSS and Airbyte Cloud

To set up this connector, you need:

- Name of the dataset to be synced
- Data API Agent user name, client access key ID, and secret key for the Data API Agent user
- Data key (API key) for the customer organization

## Setup guide

### Step 1: Nexus Configuration

#### Step 1.1: Create Nexus Customer Organization

1. Create customer organization in the nexus platform

#### Step 1.2: Configure Data Mesh in the Customer Organization

1. Log into the admin side of the Nexus application.
2. Set up the Data Mesh rule for the organization.
3. Create users with the Data Mesh privileges.
4. Make sure this user can log in to the Nexus platform.

#### Step 1.3: Configure export data pipeline in Nexus

1. Log into the Nexus platform using the user created in Step 1.2.
2. Go to **Analytics** > **Data Mesh Console**.
3. Click the **Export** tab to view exportable datasets.
4. Click **Create** to create a new export pipeline using the existing models.
5. Schedule the dataset to run.

#### Step 1.4: Summary

After completing the Nexus configuration, you should have:

- Base URL for the Nexus platform
- Nexus customer organization with a user who has the appropriate rights
- An export dataset configured
- Data API Agent user (DAPI user)
- DAPI user ID, access key ID, and secret key
- Data key (API key)

### Step 2: Set up the source connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Infor Nexus** from the Source type dropdown and enter a name for this connector.
4. Enter the **Base URL** for your Nexus platform.
5. Enter the **Dataset Name** to sync.
6. Select the **Infor Streaming Mode** (Full or Incremental).
7. Enter the **User ID** for the Data API Agent user.
8. Enter the **Access Key ID** for the Data API Agent user.
9. Enter the **Secret Key** for the Data API Agent user.
10. Enter the **API Key** for your organization.
11. Click **Set up source**.

#### For Airbyte OSS:

1. Navigate to the Airbyte UI in your browser.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Infor Nexus** from the Source type dropdown and enter a name for this connector.
4. Enter the **Base URL** for your Nexus platform.
5. Enter the **Dataset Name** to sync.
6. Select the **Infor Streaming Mode** (Full or Incremental).
7. Enter the **User ID** for the Data API Agent user.
8. Enter the **Access Key ID** for the Data API Agent user.
9. Enter the **Secret Key** for the Data API Agent user.
10. Enter the **API Key** for your organization.
11. Click **Set up source**.

### Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | The base URL of the Infor Nexus datasets API. |  |
| `dataset_name` | `string` | The name of the dataset to export. |  |
| `mode` | `string` | The Infor streaming mode. Use `Full` to sync all data or `Incremental` to sync only changes since the last sync. | `Full` |
| `user_id` | `string` | The user ID for the Data API Agent user configured in Nexus. |  |
| `access_key_id` | `string` | The access key ID for the Data API Agent user. |  |
| `secret_key` | `string` | The secret key for HMAC authentication. |  |
| `api_key` | `string` | The Infor Data API key for the organization. |  |



### Supported sync modes

The Nexus Datasets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

### Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| datasets | ❌ | DefaultPaginator | ✅ |  ✅  |

### Authentication

This connector uses HMAC (Hash-based Message Authentication Code) authentication. For each API request, the connector computes a hashed signature using your secret key and submits it in the Authorization header along with the `x-dapi-date` and `x-nexus-api-key` headers.

For more details about HMAC authentication, see the [Infor Nexus HMAC documentation](https://developer.infornexus.com/api/authentication-choices/hmac).

### Response status codes

The Infor Nexus API returns the following status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Dataset is ready and data is being streamed. |
| 202 | Dataset is not ready yet. Try again later. |
| 304 | Dataset is not ready. Check the source configuration. |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.0 | 2026-02-03 | [69349](https://github.com/airbytehq/airbyte/pull/69349) | Initial release of the Infor Nexus Datasets source connector |

</details>
