# Nexus Datasets Source Connector

Syncs data from the [GT Nexus Data API](https://developer.gtnexus.com/) into Airbyte. The connector authenticates using HMAC signatures and supports both full and incremental sync modes.

---

## Prerequisites

Before configuring the connector, ensure the following are in place in your Nexus environment:

- A Nexus customer organization with **Data Mesh** rights
- An **Export Data Set** created within that organization
- A **Data API Agent (DAPI) user** configured with the appropriate privileges

---

## Nexus Setup

### 1. Create a Customer Organization

Create a customer organization in the Nexus platform if one does not already exist.

### 2. Configure Data Mesh

1. Log into the **admin side** of the Nexus application.
2. Set up the **Data Mesh rule** for the organization.
3. Create one or more users with **Data Mesh privileges**.
4. Verify that the user can log into the Nexus platform.

### 3. Create an Export Data Pipeline

1. Log into the Nexus platform as the Data Mesh user created above.
2. Navigate to **Analytics → Data Mesh Console**.
3. Click the **Export** tab to view exportable data sets.
4. Click **Create** and build a new export pipeline using an existing model.
5. Note the **Model Name** — you will need it during connector configuration.
6. Schedule the data set to run.

### 4. Collect Configuration Values

Before setting up the connector, gather the following from your Nexus environment:

| Value | Description |
|---|---|
| Base URL | The base URL of your Nexus platform instance |
| Dataset Name | The name of the data set to sync |
| Model Name | The model name associated with the export pipeline |
| DAPI User ID | The user ID for the Data API Agent user |
| Access Key ID | The access key ID for the DAPI user |
| Secret Key | The secret key for the DAPI user |
| Data Key (API Key) | The API key for the customer organization |

---

## Connector Setup

### Airbyte Cloud

1. Log into [Airbyte Cloud](https://cloud.airbyte.com/workspaces).
2. In the left navigation, click **Sources**, then **+ New source** in the top-right.
3. Select **Nexus Datasets** from the Source type dropdown and give the connector a name.
4. Fill in all configuration fields (see [Configuration](#configuration) below).
5. Click **Set up source**.

### Airbyte OSS

1. Open your local Airbyte instance.
2. In the left navigation, click **Sources**, then **+ New source** in the top-right.
3. Select **Nexus Datasets** from the Source type dropdown and give the connector a name.
4. Fill in all configuration fields (see [Configuration](#configuration) below).
5. Click **Set up source**.

---

## Configuration

| Field | Type | Description | Default |
|---|---|---|---|
| `base_url` | string | Base URL of the Nexus platform instance | — |
| `dataset_name` | string | Name of the data set to sync | — |
| `dataset_model_name` | string | Model name for the export data pipeline | — |
| `infor_streaming_mode` | string | Sync mode: `full` or `incremental` | `full` |
| `user_id` | string | DAPI Agent user ID | — |
| `access_key_id` | string | Access key ID for the DAPI Agent user | — |
| `secret_key` | string | Secret key for the DAPI Agent user | — |
| `api_key` | string | Data API key for the organization | — |

---

## Supported Sync Modes

| Mode | Supported |
|---|---|
| Full Refresh | ✅ |
| Incremental | ✅ |

---

## Streams

| Stream | Primary Key | Pagination | Full Refresh | Incremental |
|---|---|---|---|---|
| `datasets` | — | DefaultPaginator | ✅ | ✅ |

---

## Authentication

The connector uses **HMAC (Hash-based Message Authentication Code)** authentication, implemented in the `NexusCustomAuthenticator` component. For each API request, a cryptographic signature is computed using the secret key and submitted in the `Authorization` header — no session tokens or cookies are involved.

For full details on computing the HMAC signature, refer to the [Infor Nexus HMAC authentication documentation](https://developer.infornexus.com/api/authentication-choices/hmac).

---

## API Response Codes

| Code | Meaning |
|---|---|
| `200` | Data set is ready to stream |
| `202` | Data set is not yet ready — retry later |
| `304` | Data set is not ready — check the data source |
| `404` | Not found — verify your configuration values |

---

## Changelog

| Version | Date | Pull Request | Notes |
|---|---|---|---|
| 0.1.4 | 2026-04-06 | | Dynamic schema discovery |
| 0.1.3 | 2026-02-17 | [#73548](https://github.com/airbytehq/airbyte/pull/73548) | Update dependencies |
| 0.1.2 | 2026-02-10 | [#73030](https://github.com/airbytehq/airbyte/pull/73030) | Update dependencies |
| 0.1.1 | 2026-02-03 | [#72789](https://github.com/airbytehq/airbyte/pull/72789) | Add missing `registryOverrides` to `metadata.yaml` |
| 0.1.0 | 2025-09-30 | [#69349](https://github.com/airbytehq/airbyte/pull/69349) | Initial release |
