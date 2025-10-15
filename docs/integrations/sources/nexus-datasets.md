# Nexus Datasets
Nexus datasets is a solution to sync up with the current nexus data sets API.
Data can be extracted from the nexus API after providing the required data in the config.
Data set name should be provided aliong with the other details to sync the data.
[API Documentation](https://developer.gtnexus.com/)

## Prerequisites

- Nexus customer organization with Data Mesh rights
- Export data set created in the customer organization
- Data API Agent user configured in the customer organization

## Airbyte OSS and Airbyte Cloud

- Name of the data set to be synced
- Data API Agent user name / Cliend access key ID / Secret key for the Data API Agent user
- Data Key (API Key) for the customer organization

## Setup guide

### Step 1: Nexus Configuration

#### Step 1.1: Create Nexus Customer Organization

1. Create customer organization in the nexus platform

#### Step 1.2: Configure Data Mesh in the Customer Organization

1. Log into the admin side of the nexus application
2. Set up the Data Mesh rule for the organization
3. Create users with the Data Mesh previledges
4. Make sure this user can be logged in to the nexus platfrom

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

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.
4. Add **Base URL**
5. Add **User ID**
6. Add **Access Key ID**
7. Add **Secret Key**
8. Add **API Key**
9. Add **Dataset Name**
10. Add **File Type**
11. Add **Mode**
12. Click `Set up source`.

### For Airbyte OSS:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.
4. Add **Base URL**
5. Add **User ID**
6. Add **Access Key ID**
7. Add **Secret Key**
8. Add **API Key**
9. Add **Dataset Name**
10. Add **File Type**
11. Add **Mode**
12. Click `Set up source`.

### Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `base_url` | `string` | Base URL. Enter base url for your data set |  |
| `user_id` | `string` | Data API agent user ID. Enter DAPI agent user id configured in the nexus |  |
| `access_key_id` | `string` | Access key ID. Enter access key ID for the DAPI agent user |  |
| `secret_key` | `string` | Secret key. Enter secret key for the DAPI agent user |  |
| `api_key` | `string` | Data API key. Enter data API key for the organization |  |
| `dataset_name` | `string` | Name of the dataset. Enter dataset name to be synced |  |
| `file_type` | `string` | File type. Type of the file to be synced, ex. JSONL / PARQUET / CSV |  |
| `mode` | `string` | Sync mode. Full or Incremental | Full |


## Supported sync modes

The Nexus Datasets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| datasets | ❌ | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-09-30 |  | Nexus datasets connector first version |



</details>
