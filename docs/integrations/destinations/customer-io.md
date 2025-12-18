# Customer.io

This page contains the setup guide and reference information for the Customer.io destination connector.

## Overview

The Customer.io destination connector allows you to sync data to Customer.io, a customer data management platform. This connector supports [data activation](/platform/move-data/elt-data-activation).

## Prerequisites

- A Customer.io Account
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

### Destination Objects + Operations

Here are the destination objects and their respective operations that are currently supported:

- [Person](https://docs.customer.io/journeys/create-update-person/): Identifies a person and assigns traits to them.
- [Person Events](https://docs.customer.io/journeys/events/): Track an event for a user that is known or not by Customer.io. Required fields: `person_email`, `event_name`. Optional fields: `event_id` (for event deduplication), `timestamp`.

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync            | Yes        |
| Incremental - Append Sync    | Yes        |
| Incremental - Dedupe Sync    | Yes        |
| Namespaces                   | Yes        |

### Restrictions

- Each entry sent to the API needs to be 32kb or smaller
- Customer.io allows you to send unstructured attributes. Those attributes are subject to the following restrictions:
    - Max number of attributes allowed per object is 300
    - Max size of all attributes is 100kb
    - The attributes name is 150 bytes or smaller
    - The value of attributes is 1000 bytes or smaller
- Event names are 100 bytes or smaller

## Getting started

### Setup guide

In order to configure this connector, you need to generate your Track API Key and obtain your Site ID from Customer.io (Workspace Settings → API and webhook credentials → Create Track API Key). Once this is done, provide both the Site ID and API Key in the connector's configuration and you are good to go.

**Object Storage for Rejected Records**: This connector supports data activation and can optionally store [rejected records](/platform/move-data/rejected-records) in object storage (such as S3). Configure object storage in the connector settings to capture records that couldn't be synced to Customer.io due to schema validation issues or other errors.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                                   |
|:--------|:-----------|:----------------------------------------------------------|:----------------------------------------------------------|
| 0.0.8 | 2025-11-01 | [69132](https://github.com/airbytehq/airbyte/pull/69132) | Upgrade to Bulk CDK 0.1.61. |
| 0.0.7   | 2025-09-23 | [66571](https://github.com/airbytehq/airbyte/pull/66571)      | Fix person_identify in incremental mode                   |
| 0.0.6   | 2025-09-16 | [tbd](https://github.com/airbytehq/airbyte/pull/tbd)      | Use low-code discover definition and pin to a CDK version |
| 0.0.5   | 2025-09-08 | [65157](https://github.com/airbytehq/airbyte/pull/65157)  | Update following breaking changes on spec                 |
| 0.0.4   | 2025-08-20 | [#65113](https://github.com/airbytehq/airbyte/pull/65113) | Update logo                                               |
| 0.0.3   | 2025-07-08 | [#62848](https://github.com/airbytehq/airbyte/pull/62848) | Improve UX on connector configuration                     |
| 0.0.2   | 2025-07-08 | [#62843](https://github.com/airbytehq/airbyte/pull/62843) | Checker should validate DLQ                               |
| 0.0.1   | 2025-07-07 | [#62083](https://github.com/airbytehq/airbyte/pull/62083) | Initial release of the Customer.io destination connector  |
