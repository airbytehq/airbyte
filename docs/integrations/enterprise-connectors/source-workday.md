# Source Workday

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, provide enhanced capabilities and support for critical enterprise systems. To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte's [Workday](https://workday.com) enterprise source connector currently offers the following features:

* Incremental as well as Full Refresh [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes). Note that incremental syncs are only supported for specific streams.
* Reliable replication at any size with [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).
* Support for both REST API and Workday Report-as-a-Service (RaaS) streams. Each provided Report ID can be used as a separate stream with an auto-detected schema. Note that a separate Source must be created to use RaaS streams in addition to REST API streams.

## Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         | 
| SSL connection                | Yes        |
| Namespaces                    | No         | 

## Prerequisites

* Workday tenant - The Organization ID for your Workday environment. This can be found by logging into your Workday account and going to My Account > Organization ID
* Workday hostname - The endpoint for connecting into your Workday environment. This can be found by logging into your Workday instance and searching “Public Web Service” in the search bar and selecting the appropriate report. Use the ellipse (...) button to select **Web Service > View WSDL**

* For REST API streams:
	* Access token - An OAuth 2.0 access token for API client integrations. More information and instructions can be found in the Workday community documentation for your environment about creating and registering a Workday API Client. If you are using Airbyte Teams, when registering the API Client for Airbyte you can use https://cloud.airbyte.com/auth_flow for the Redirection URI field . If you are using Self-Managed Enterprise, you can use the URL of your Airbyte deployment instead.

* For Report-as-a-Service (RaaS) streams:
	* Workday username and password - A user account that has the necessary permissions to access the reports you want to sync.
	* Report IDs - Each report in Workday has a unique Report ID.

## Setup Guide

### For REST API streams

1. Log into your Airbyte Cloud account.
2. Click Sources and then click **+ New source**.
3. On the Set up the source page, select Workday.
4. Enter a name for the Workday connector.
5. Enter the Tenant and Hostname for your Workday environment.
6. Select the option for **REST API Streams**.
7. Enter the access token.
8. **Start Date (Optional)** is the earliest date for data that will be synced. If a date is not specified, all data from the last 2 years will be synced.
9. Click Set up source.

![REST Setup](https://raw.githubusercontent.com/airbytehq/airbyte/refs/heads/master/docs/enterprise-setup/assets/enterprise-connectors/workday-rest.png)


### For RaaS streams

1. Log into your Airbyte Cloud account.
2. Click Sources and then click **+ New source**.
3. On the Set up the source page, select Workday
4. Enter a name for the Workday connector.
5. Enter the Tenant and Hostname for your Workday environment.
6. Select the option for **Report Based Streams**.
7. Enter the username and password of the Workday account that can access your desired reports.
8. Enter the Report IDs for the reports you want to sync with this connector.
9. Click **Set up source**.

![RaaS Setup](https://raw.githubusercontent.com/airbytehq/airbyte/refs/heads/master/docs/enterprise-setup/assets/enterprise-connectors/workday-raas.png)

## Supported sync modes

The Workday source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

* Full Refresh
* Incremental for the following REST API streams:
	* Worker Payslips
	* Worker Time Off Entries

## Supported Streams

The Workday connector supports the following REST API streams:

* Jobs
* Job Families
* Job Profiles
* People
* Workers
* Workers Direct Reports
* Worker History
* Worker Payslips (Incremental)
* Worker Time Off Entries (Incremental)


## Changelog

<details>
  <summary>Expand to review</summary>

The connector is still incubating, this section only exists to satisfy Airbyte's QA checks.

- 0.2.0
- 0.1.0

</details>
