---
description: Export entities from Google Cloud Datastore to any Airbyte destination.
---

# Google Cloud Datastore

## Overview

[Google Cloud Datastore](https://cloud.google.com/datastore/docs) is a highly scalable NoSQL document database built for automatic scaling and high performance. This connector exports entities from any configured Datastore Kind and syncs them to your chosen destination.

Each Kind becomes one Airbyte stream. Schema is inferred automatically at discovery time by sampling up to 100 entities per Kind.

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | Yes        |

### Output schema

Every record contains the following guaranteed fields plus all entity properties:

| Field        | Type   | Description                                        |
| :----------- | :----- | :------------------------------------------------- |
| `_key`       | string | Flat string representation of the entity key path |
| `_kind`      | string | Kind this entity belongs to                        |
| `_namespace` | string | Datastore namespace (empty string = default)       |

Datastore-specific types are serialized as follows:

| Datastore type | Serialized as                    |
| :------------- | :------------------------------- |
| `datetime`     | ISO 8601 string (UTC)            |
| `Key`          | Flat path string, e.g. `Kind/id` |
| `bytes`        | Base64-encoded string            |

## Getting started

### Prerequisites

- A GCP project with Cloud Datastore (or Firestore in Datastore mode) enabled
- A GCP service account with the **Cloud Datastore User** role (`roles/datastore.user`) on the target project
- The full JSON key file for that service account

### Setup guide

1. In the GCP Console, navigate to **IAM & Admin → Service Accounts**.
2. Create a service account (or use an existing one) and grant it the `roles/datastore.user` role.
3. Create a JSON key for the service account and download it.
4. In Airbyte, go to **Sources → New Source** and select **Google Cloud Datastore**.
5. Fill in:
   - **GCP Project ID**: your GCP project ID
   - **Service Account Credentials JSON**: paste the entire contents of the downloaded key file
   - **Namespace** _(optional)_: the Datastore namespace to query (leave empty for the default namespace)
   - **Kinds**: the list of entity Kinds to sync (at least one required)
6. Click **Test and Save**.

### Incremental sync

Set the **cursor field** to a datetime or numeric property that increases monotonically (e.g. `updated_at`). The connector will filter entities where `cursor_field >= last_synced_value`.

The recommended destination sync mode is **Append + Dedupe** on `_key`.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject           |
| :------ | :--------- | :------------------------------------------------------- | :---------------- |
| 0.1.0   | 2026-06-02 | [78532](https://github.com/airbytehq/airbyte/pull/78532) | Initial release   |

</details>
