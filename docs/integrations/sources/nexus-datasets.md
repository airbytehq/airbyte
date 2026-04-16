# Infor Nexus Datasets

<HideInUI>

This page contains the setup guide and reference information for the [Infor Nexus](https://developer.infornexus.com/) source connector.

</HideInUI>

The Infor Nexus Datasets source connector syncs data from [Infor Nexus](https://developer.infornexus.com/) Data Mesh export datasets using the Infor Nexus Data API (v3.1) with HMAC authentication.

## Prerequisites

- An Infor Nexus customer organization with Data Mesh rights
- An export dataset created in the customer organization
- A Data API (DAPI) agent user configured in the customer organization
- The following credentials for the DAPI agent user:
  - User ID
  - Client access key ID
  - Secret key
- A Data Key (API Key) for the customer organization

## Setup guide

### Step 1: Configure Infor Nexus

#### Create a customer organization

Create a customer organization in the Infor Nexus platform.

#### Configure Data Mesh

1. Log into the admin console of your Infor Nexus application.
2. Set up the Data Mesh rule for your organization.
3. Create a user with Data Mesh privileges.
4. Verify this user can log into the Infor Nexus platform.

#### Create an export dataset

1. Log into the Infor Nexus platform with the user you created.
2. Go to **Analytics** > **Data Mesh Console**.
3. Click the **Export** tab to view exportable datasets.
4. Click **Create** to create a new export pipeline from the existing models.
5. Schedule the dataset to run.

#### Gather your credentials

Before configuring Airbyte, collect the following information:

- Base URL for your Infor Nexus platform
- Dataset name
- DAPI agent user ID
- DAPI agent access key ID
- DAPI agent secret key
- Data key (API key) for your organization

For more information about HMAC authentication, see the [Infor Nexus HMAC documentation](https://developer.infornexus.com/api/authentication-choices/hmac).

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources**, then click **+ New source**.
3. Select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources**, then click **+ New source**.
3. Select **Nexus Datasets** from the Source type dropdown and enter a name for this connector.

<!-- /env:oss -->

<FieldAnchor field="base_url">

1. Enter the **Base URL** for your Infor Nexus platform.

</FieldAnchor>

<FieldAnchor field="dataset_name">

1. Enter the **Dataset Name** to sync.

</FieldAnchor>

<FieldAnchor field="mode">

1. Select the **Infor Streaming Mode**. Choose `Full` for a complete dataset export, or `Incremental` for changes only. The default is `Full`.

</FieldAnchor>

<FieldAnchor field="user_id">

1. Enter the **User ID** for your DAPI agent user.

</FieldAnchor>

<FieldAnchor field="access_key_id">

1. Enter the **Access Key ID** for your DAPI agent user.

</FieldAnchor>

<FieldAnchor field="secret_key">

1. Enter the **Secret Key** for your DAPI agent user.

</FieldAnchor>

<FieldAnchor field="api_key">

1. Enter the **API Key** (Data Key) for your organization.

</FieldAnchor>

1. Click **Set up source**.

### Configuration reference

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `base_url` | `string` | Yes | The base URL of your Infor Nexus platform. | |
| `dataset_name` | `string` | Yes | The name of the dataset to export. | |
| `mode` | `string` | No | The streaming mode: `Full` exports the complete dataset; `Incremental` exports only changes since the last export. | `Full` |
| `user_id` | `string` | Yes | The DAPI agent user ID configured in Infor Nexus. | |
| `access_key_id` | `string` | Yes | The access key ID for the DAPI agent user. | |
| `secret_key` | `string` | Yes | The secret key for HMAC authentication. | |
| `api_key` | `string` | Yes | The Data API key for your organization. | |

<HideInUI>

## Supported sync modes

The Infor Nexus Datasets source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| datasets | None | Yes | Yes | Yes |

The `datasets` stream returns records from the configured Infor Nexus export dataset. Each record contains the following fields:

- `raw_data`: The record payload as a JSON object.
- `raw_data_string`: The record payload as a JSON string.

## Limitations and troubleshooting

### API response codes

The Infor Nexus Data API returns the following status codes during dataset export:

| Status Code | Meaning | Recommended action |
|-------------|---------|-------------------|
| 200 | Dataset is ready to stream. | No action needed. |
| 202 | Dataset is not yet ready. | Wait and retry the sync later. |
| 304 | Dataset is not ready. | Contact Infor member services to investigate. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.1.4 | 2026-04-09 | [76138](https://github.com/airbytehq/airbyte/pull/76138) | Add missing imports for AirbyteTracedException and FailureType in components.py |
| 0.1.3 | 2026-02-17 | [73548](https://github.com/airbytehq/airbyte/pull/73548) | Update dependencies |
| 0.1.2 | 2026-02-10 | [73030](https://github.com/airbytehq/airbyte/pull/73030) | Update dependencies |
| 0.1.1 | 2026-02-03 | [72789](https://github.com/airbytehq/airbyte/pull/72789) | Add missing registryOverrides to metadata.yaml |
| 0.1.0 | 2025-09-30 | [69349](https://github.com/airbytehq/airbyte/pull/69349) | Initial release of the Infor Nexus Datasets connector |

</details>

</HideInUI>
