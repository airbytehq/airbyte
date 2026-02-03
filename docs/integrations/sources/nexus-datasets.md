# Nexus Datasets

The Nexus Datasets connector syncs data from the Infor Nexus Data Mesh API. You can extract data from the Nexus API by providing the required configuration, including the dataset name and authentication credentials.

For more information, see the [Infor Nexus API Documentation](https://developer.infornexus.com/api).

## Prerequisites

- Nexus customer organization with Data Mesh rights
- Export data set created in the customer organization
- Data API Agent user configured in the customer organization

## Airbyte OSS and Airbyte Cloud

- Name of the data set to be synced
- Data API Agent user name, client access key ID, and secret key for the Data API Agent user
- Data Key (API Key) for the customer organization

## Setup guide

### Step 1: Nexus Configuration

#### Step 1.1: Create Nexus Customer Organization

1. Create customer organization in the nexus platform

#### Step 1.2: Configure Data Mesh in the Customer Organization

1. Log into the admin side of the nexus application
2. Set up the Data Mesh rule for the organization
3. Create users with the Data Mesh privileges
4. Make sure this user can log in to the Nexus platform

#### Step 1.3: Configure export data pipeline in the Nexus

1. Log into the nexus platform using created user in the step 2
2. Go to **Analytics** » **Data Mesh Console**
3. Click on **Export** tab to go into the exportable data sets
4. Click **Create** to create new export pipeline using the existing models
5. Schedule the data set to run

#### Step 1.4: Summary

- Base URL for the nexus platform
- Nexus customer organization with relevant user with rights
- Export data set
- Data API Agent user (DAPI user)
- DAPI user id / access key id / secret key
- Data key (API key)

### Step 2: Set up the source connector in Airbyte

#### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.
4. Add **Base URL**
5. Add **Dataset Name**
6. Add **Infor Streaming Mode (default Full)**
7. Add **User ID**
8. Add **Access Key ID**
9. Add **Secret Key**
10. Add **API Key**
11. Click **Set up source**.

#### For Airbyte OSS

1. Log into your Airbyte OSS instance.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.
4. Add **Base URL**
5. Add **Dataset Name**
6. Add **Infor Streaming Mode (default Full)**
7. Add **User ID**
8. Add **Access Key ID**
9. Add **Secret Key**
10. Add **API Key**
11. Click **Set up source**.

### Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | The base URL of the Infor Nexus datasets API. |  |
| `dataset_name` | `string` | The name of the dataset to export. |  |
| `mode` | `string` | Infor streaming mode. Set to `Full` for a complete data export or `Incremental` for changes only. | `Full` |
| `user_id` | `string` | The Data API agent user ID configured in Nexus. |  |
| `access_key_id` | `string` | The access key ID for the DAPI agent user. |  |
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

### Custom Components

NexusCustomAuthenticator is a primary component which handles the HMAC authentication for nexus API.

HMAC stands for Hash-based Message Authentication Code. In HMAC authentication, every request is independently established using a cryptographic hash function. For each API request, the client computes a hashed "signature" using a secret key and submits it in the Authorization header.

Please refer https://developer.infornexus.com/api/authentication-choices/hmac for more details to get the data to calculate the HMAC signature.

### Response codes

The connector handles the following HTTP response codes from the Nexus API:

| Code | Meaning |
|------|---------|
| 200 | Success. The dataset is ready and data is being streamed. |
| 202 | The dataset is not ready yet. The connector will retry later. |
| 304 | The dataset is not ready. Check the source configuration and try again. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.1 | 2026-02-03 | [72789](https://github.com/airbytehq/airbyte/pull/72789) | Add missing registryOverrides to metadata.yaml |
| 0.1.0 | 2026-02-03 | [69349](https://github.com/airbytehq/airbyte/pull/69349) | Initial release of the Nexus Datasets connector |

</details>
