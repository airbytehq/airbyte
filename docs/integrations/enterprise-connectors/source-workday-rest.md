---
dockerRepository: airbyte/source-workday-rest
enterprise-connector: true
---
# Source Workday REST

Airbyte's [Workday](https://workday.com) enterprise source connector currently offers the following features:

- Incremental as well as Full Refresh [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes). Note that incremental syncs are only supported for specific streams.
- Reliable replication at any size with [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).
- Support for REST API Workday streams.

## Features

| Feature                       | Supported? |
|:------------------------------|:-----------|
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Prerequisites

- Workday tenant - The Organization ID for your Workday environment. This can be found by logging into your Workday account and going to My Account > Organization ID
- Workday hostname - The endpoint for connecting into your Workday environment. This can be found by logging into your Workday instance and searching “Public Web Service” in the search bar and selecting the appropriate report. Use the ellipse (...) button to select **Web Service > View WSDL**
- Access token - An OAuth 2.0 access token for API client integrations. More information and instructions can be found in the Workday community documentation for your environment about creating and registering a Workday API Client. If you are using Airbyte Teams, when registering the API Client for Airbyte, you can use https://cloud.airbyte.com/auth_flow for the Redirection URI field . If you are using Self-Managed Enterprise, you can use the URL of your Airbyte deployment instead.

## Setup Guide

1. Log into your Airbyte Cloud account.
2. Click Sources and then click **+ New source**.
3. On the Set up the source page, select Workday REST.
4. Enter a name for the Workday connector.
5. Enter the Tenant and Hostname for your Workday environment.
6. Enter the access token.
7. **Start Date (Optional)** is the earliest date for data that will be synced. If a date is not specified, all data from the last 2 years will be synced.
8. Click Set up source.

## Supported sync modes

The Workday REST source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental for the following streams:
  - Worker Payslips
  - Worker Time Off Entries

## Supported Streams

The Workday REST connector supports the following streams:

- Jobs
- Job Families
- Job Profiles
- People
- Workers
- Workers Direct Reports
- Worker History
- Worker Payslips (Incremental)
- Worker Time Off Entries (Incremental)

## Changelog

<details>
  <summary>Expand to review</summary>

- 0.1.0

</details>
