---
dockerRepository: airbyte/source-workday
enterprise-connector: true
---
# Source Workday

Airbyte's [Workday](https://workday.com) enterprise source connector currently offers the following features:

- Full Refresh [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes). Note that incremental syncs are only supported for specific streams.
- Reliable replication at any size with [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).
- Support for Workday Report-as-a-Service (RaaS) streams. Each provided Report ID can be used as a separate stream with an auto-detected schema.

## Features

| Feature                       | Supported? |
|:------------------------------|:-----------|
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Prerequisites

- Workday tenant - The Organization ID for your Workday environment. This can be found by logging into your Workday account and going to My Account > Organization ID
- Workday hostname - The endpoint for connecting into your Workday environment. This can be found by logging into your Workday instance and searching “Public Web Service” in the search bar and selecting the appropriate report. Use the ellipse (...) button to select **Web Service > View WSDL**
- Workday username and password - A user account that has the necessary permissions to access the reports you want to sync.
- Report IDs - Each report in Workday has a unique Report ID.

## Setup guide

1. Log into your Airbyte Cloud account.
2. Click Sources and then click **+ New source**.
3. On the Set up the source page, select Workday
4. Enter a name for the Workday connector.
5. Enter the Tenant and Hostname for your Workday environment.
6. Enter the username and password of the Workday account that can access your desired reports.
7. Enter the Report IDs for the reports you want to sync with this connector.
8. Click **Set up source**.

## Supported sync modes

The Workday source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh

## Supported streams

The Workday connector supports dynamic streams based on report ids provided in the source set up.

## Changelog

<details>
  <summary>Expand to review</summary>

- 1.0.0
- 0.2.1
- 0.2.0
- 0.1.0

</details>
