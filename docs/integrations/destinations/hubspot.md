---
dockerRepository: airbyte/destination-hubspot
---

# HubSpot Destination

This page guides you through setting up the [HubSpot](https://www.hubspot.com/) destination connector. This connector supports [data activation](/platform/move-data/elt-data-activation) for operational workflows.

## Prerequisites

- A HubSpot account with a [HubSpot app](https://developers.hubspot.com/docs/api/oauth-quickstart-guide) configured for OAuth authentication
- Airbyte version 1.8 or later, or Airbyte Cloud
- For Custom Objects: a HubSpot Enterprise subscription

### S3 prerequisites for rejected records

If you're using an S3 bucket to store rejected records, you also need the following.

1. Allow connections from Airbyte to your AWS S3/Minio S3 cluster (if they exist in separate VPCs).
2. [Enforce encryption of data in transit](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html#transit).
3. An S3 bucket with credentials, a Role ARN, or an instance profile with read/write permissions configured for the host (EC2, EKS).

    - These fields are always required:

      - **S3 Bucket Name**
      - **S3 Bucket Region**
      - **Prefix Path in the Bucket**

    - If you are using STS Assume Role, you must provide:

      - **Role ARN**

    - If you are using AWS credentials, you must provide:

      - **Access Key ID**
      - **Secret Access Key**

    - If you are using an Instance Profile, you may omit the Access Key ID, Secret Access Key, and Role ARN.

## Setup guide

### Set up the HubSpot connector in Airbyte

1. Log into your Airbyte account.
2. Click Destination and then click + New destination.
3. On the Set up the destination page, select HubSpot from the Destination tiles.
4. Enter a name for the HubSpot connector.
5. Click **Authenticate your HubSpot account** to sign in with HubSpot and authorize your account. This connector uses OAuth for authentication.

   :::note
   You may encounter an error during authentication with the message `An invalid scope name was provided`. To resolve this, close the popup window and retry authentication.
   :::

6. Click **Set up destination** and wait for the tests to complete.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | No |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

This is a [data activation](/platform/move-data/elt-data-activation) destination. In addition to the Airbyte sync modes above, HubSpot supports per-object write operations (insert, upsert, update, and soft delete) configured in the connection settings.

## Supported Objects

The HubSpot destination connector supports the following objects:

- [Companies](https://developers.hubspot.com/docs/api/crm/companies): Upsert on unique property
- [Contacts](https://developers.hubspot.com/docs/api/crm/contacts): Upsert on email
- [Deals](https://developers.hubspot.com/docs/api/crm/deals): Upsert on unique property
- [Products](https://developers.hubspot.com/docs/api/crm/products): Upsert on unique property
- [Custom Objects](https://developers.hubspot.com/docs/guides/api/crm/objects/custom-objects): Upsert on unique property (requires HubSpot Enterprise)

## Limitations & Troubleshooting

### Rate limiting

The connector respects [HubSpot's API rate limits](https://developers.hubspot.com/docs/api/usage-details). Rate limits depend on your HubSpot subscription tier. For public OAuth apps, each account is limited to 110 requests every 10 seconds. If the connector encounters rate limiting, it retries requests with exponential backoff.

### Batch size

The connector sends records to HubSpot in batches of up to 100 records per API call. This is the maximum batch size supported by the HubSpot batch upsert API.

### Destination object not showing up

Except for Contacts, which use email as the matching key, the upsert method for this connector requires a unique value property on the destination object.

**Matching key requirements:**

- **Contacts**: Uses the email property automatically.
- **All other objects**: Require a property with unique values enabled.

To create a unique value property in HubSpot:

1. In the left sidebar, select the CRM object you want to sync to.
2. Under **Actions**, select **Edit Properties**.
3. Click **Create property**.
4. When entering the rules, check **Require unique values for this property**.

### App verification

HubSpot requires [more than 60 installations](https://developers.hubspot.com/docs/guides/apps/marketplace/certification-requirements#value) to verify an app. When installing the app, you might see the message "You're connecting to an unverified app." This is expected and doesn't affect functionality.

### Scopes for unsupported objects

During app installation, you might see scopes related to objects this connector does not yet support. This is expected. Changing scopes would require you to re-authenticate, so scopes for planned objects are included in advance.

### 403 Forbidden error

HubSpot requires specific [OAuth scopes](https://developers.hubspot.com/docs/api/working-with-oauth#scopes) for each API endpoint. Each object type requires access to its corresponding scope. If you receive a 403 error, verify that your OAuth app has the required scopes for the objects you are syncing.

### Supported property types

The connector maps the following HubSpot property types:

| HubSpot type   | Mapped type             |
| :------------- | :---------------------- |
| `string`       | String                  |
| `enumeration`  | String                  |
| `phone_number` | String                  |
| `number`       | Number                  |
| `bool`         | Boolean                 |
| `date`         | Date                    |
| `datetime`     | Timestamp with timezone |

Properties with types not in the preceding table, such as `object_coordinates`, read-only properties, and calculated properties, are excluded from the sync.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                    | Subject                                             |
|:--------|:-----------|:----------------------------------------------------------------|:----------------------------------------------------|
| 0.0.11  | 2026-04-15 | [76336](https://github.com/airbytehq/airbyte/pull/76336)        | Upgrade Bulk CDK to 1.0.8 (OAuth token expiry fix)  |
| 0.0.10  | 2026-02-09 | [72975](https://github.com/airbytehq/airbyte/pull/72975)        | Upgrade CDK to 1.0.1                                |
| 0.0.9   | 2026-01-26 | [72304](https://github.com/airbytehq/airbyte/pull/72304)        | Upgrade CDK to 0.2.0                                |
| 0.0.8   | 2025-11-05 | [69131](https://github.com/airbytehq/airbyte/pull/69131)        | Upgrade to Bulk CDK 0.1.61.                         |
| 0.0.7   | 2025-09-24 | [66684](https://github.com/airbytehq/airbyte/pull/66684)        | Pin to CDK artifact                                 |
| 0.0.6   | 2025-09-10 | [65986](https://github.com/airbytehq/airbyte/pull/65986)        | Adding product object                               |
| 0.0.5   | 2025-09-08 | [65157](https://github.com/airbytehq/airbyte/pull/65157)        | Update following breaking changes on spec           |
| 0.0.4   | 2025-07-31 | [64144](https://github.com/airbytehq/airbyte/pull/64144)        | OSS release                                         |
| 0.0.3   | 2025-07-18 | [205](https://github.com/airbytehq/airbyte-enterprise/pull/205) | Forcing new release                                 |
| 0.0.2   | 2025-07-18 | [204](https://github.com/airbytehq/airbyte-enterprise/pull/204) | Fixing auth                                         |
| 0.0.1   | 2025-07-18 | [201](https://github.com/airbytehq/airbyte-enterprise/pull/201) | First iteration internally                          |

</details>
