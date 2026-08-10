# Customer.io

This page contains the setup guide and reference information for the Customer.io destination connector.

## Overview

The Customer.io destination connector syncs data to [Customer.io](https://customer.io/) using the [Track API v2 batch endpoint](https://customer.io/docs/api/track/#tag/Track-v2). This connector supports [data activation](/platform/move-data/elt-data-activation), letting you identify people and track events in Customer.io from your data warehouse or other sources.

## Prerequisites

- A Customer.io account
- A Customer.io Track API Key and Site ID (see [Setup guide](#setup-guide))
- Airbyte version 1.8 or later, or Airbyte Cloud

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

To configure this connector:

1. In Customer.io, go to **Settings** > **API & Webhook Credentials**.
2. Under **Track API Keys**, click **Create Track API Key**.
3. Copy the **Site ID** and **API Key**.
4. In Airbyte, create a new Customer.io destination and enter the **Site ID** and **API Key**.

This connector uses [HTTP Basic authentication](https://customer.io/docs/api/track/#section/Authentication) with the Site ID as the username and the API Key as the password.

### Rejected records

This connector can optionally store [rejected records](/platform/move-data/rejected-records) in object storage (such as S3). Configure object storage in the connector settings to capture records that couldn't be synced to Customer.io. Records may be rejected due to payload size limits, missing required fields, or Customer.io API validation errors.

## Destination objects and operations

This connector supports two destination objects:

- **person_identify** (Upsert): [Identifies a person](https://docs.customer.io/journeys/create-update-person/) and assigns attributes to them. The `person_email` field is required and used as the matching key. All other fields in the record are sent as person attributes.
- **person_event** (Insert): [Tracks an event](https://docs.customer.io/journeys/events/) for a person. Required fields: `person_email`, `event_name`. Optional fields: `event_id` (for event deduplication), `timestamp` (Unix timestamp). All other fields are sent as event attributes.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | No |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

This is a [data activation](/platform/move-data/elt-data-activation) destination. In addition to the Airbyte sync modes above, Customer.io supports identify (person) and track (event) operations configured per stream.

## Limitations

- The connector sends data to the US region endpoint (`track.customer.io`). If your Customer.io account is in the EU region, data still reaches your workspace but passes through US servers first. See [Customer.io server addresses](https://customer.io/docs/api/track/#section/Overview/Server-addresses:-US-and-EU) for details.
- The Track API has a rate limit of 1000 requests per second. The connector batches records (up to 500 KB per batch) to stay within this limit.
- Each entry in a batch must be 32 KB or smaller.
- Customer.io applies the following attribute limits:
    - Max 300 attributes per person or identify call
    - Max 100 KB total attribute size per person
    - Attribute names: 150 bytes or smaller
    - Attribute values: 1000 bytes or smaller
- Event names must be 100 bytes or smaller.

## Namespace support

This destination does not support [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.0.11 | 2026-06-18 | [80254](https://github.com/airbytehq/airbyte/pull/80254) | Move to community support level |
| 0.0.10 | 2026-02-09 | [72973](https://github.com/airbytehq/airbyte/pull/72973) | Upgrade CDK to 1.0.1 |
| 0.0.9 | 2026-01-26 | [72303](https://github.com/airbytehq/airbyte/pull/72303) | Upgrade CDK to 0.2.0 |
| 0.0.8 | 2025-11-05 | [69132](https://github.com/airbytehq/airbyte/pull/69132) | Upgrade to Bulk CDK 0.1.61 |
| 0.0.7 | 2025-09-23 | [66571](https://github.com/airbytehq/airbyte/pull/66571) | Fix person_identify in incremental mode |
| 0.0.6 | 2025-09-18 | [66238](https://github.com/airbytehq/airbyte/pull/66238) | Use low-code discover definition and pin to a CDK version |
| 0.0.5 | 2025-09-08 | [65157](https://github.com/airbytehq/airbyte/pull/65157) | Update following breaking changes on spec |
| 0.0.4 | 2025-08-20 | [65113](https://github.com/airbytehq/airbyte/pull/65113) | Update logo |
| 0.0.3 | 2025-07-10 | [62848](https://github.com/airbytehq/airbyte/pull/62848) | Improve UX on connector configuration |
| 0.0.2 | 2025-07-08 | [62843](https://github.com/airbytehq/airbyte/pull/62843) | Checker should validate DLQ |
| 0.0.1 | 2025-07-07 | [62083](https://github.com/airbytehq/airbyte/pull/62083) | Initial release of the Customer.io destination connector |
