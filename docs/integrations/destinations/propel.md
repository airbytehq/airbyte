# Propel

## Overview

[Propel](https://propeldata.com) provides an easy way to power your analytic dashboards, reports, and workflows with low-latency data from any SaaS application or database. 

This Airbyte destination allows to sync data into a Propel Data Pool.

 > ℹ️ This destination is maintained by Propel. Please send any support requests to support@propeldata.com

## Features

| Feature                        | Supported |     |
| :----------------------------- | :-------- | :-- |
| Full Refresh Sync              | Yes       |     |
| Incremental - Append Sync      | Yes       |     |
| Incremental - Append + Deduped | No        |     |
| Namespaces                     | Yes       |     |

## Getting started

### Prerequisites

To connect Propel to Airbyte, you need the following:

- A [Propel account](https://console.propeldata.com/get-started).
- An Airbyte account.
- A Propel Application with the ADMIN scope.

---

## Setup instructions

You must create a Propel Application. Propel Applications provide the API credentials, allowing the Airbyte destination to access the Propel API.

1. Go to the **Applications** section and click **Create Application**.
2. Enter the **Unique Name**. For example, 'Airbyte Destination'.
3. Provide a **Description**. For example, 'The Airbyte Destination app'.
4. In the API scopes section, in the **Scopes** drop-down menu, select the **ADMIN** scope.
5. In the Propeller section, in the **Select Propeller** drop-down menu, select the processing power as per your requirements.
6. Click **Create**.
7. Make a note of the Application ID and secret. You will need them to configure Fivetran.

## Configuration

| Parameter  |  Type  | Notes                      |
| :--------- | :----: | :------------------------- |
| privateKey | string | You private key on Streamr |
| streamId   | string | Your full Stream ID        |

## Troubleshooting

If a sync fails to insert a record, you can review sync errors in the Propel console. Select the Data Pool to which data is being synced and select the **Error Logs** tab. 

You may send support requests to: support@propeldata.com

## CHANGELOG

| Version | Date       | Pull Request                                                       | Subject                     |
| :------ | :--------- | :----------------------------------------------------------------- | :-------------------------- |
| 0.0.1   | 2024-02-13 | [GitHub](https://github.com/propeldata/airbyte-destination/pull/1) | Initial Propel destination. |
