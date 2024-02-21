# Propel

## Overview

[Propel](https://www.propeldata.com) is an Analytics Platform as a Service for developers to effortlessly ship embedded analytics, data-serving APIs, and usage metering into their applications.

It provides developers with:

- [Serverless ClickHouse](https://www.propeldata.com/docs/connect-your-data) to serve data blazingly fast without managing any infrastructure.
- [Data serving APIs](https://www.propeldata.com/docs/query-your-data) and [React UI components](https://storybook.propeldata.com/) to build customer-facing analytics experiences.
- [Access Control policies](https://www.propeldata.com/docs/control-access/multi-tenancy) to securely serve data to authenticated users in multi-tenant environments.

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

1. Log in to the [Propel Console](https://console.propeldata.com/).
2. Go to the **Applications** section and click **Create Application**.
3. Enter the **Unique Name**. For example, "Airbyte Destination".
4. Provide a **Description**. For example, "The Airbyte Destination app".
5. In the API scopes section, in the **Scopes** drop-down menu, select the **ADMIN** scope.
6. In the Propeller section, in the **Select Propeller** drop-down menu, select the processing power as per your requirements.
7. Click **Create**.
8. Make a note of the Application ID and secret. You will need them to configure Airbyte.

## Configuration

| Parameter          |  Type  | Notes                     |
| :----------------- | :----: | :------------------------ |
| application_id     | string | Propel Application ID     |
| application_secret | string | Propel Application secret |

## Troubleshooting

If a sync fails to insert a record, you can review sync errors in the Propel console. Select the Data Pool to which data is being synced and select the **Error Logs** tab. 

You may send support requests to: support@propeldata.com

## CHANGELOG

| Version | Date       | Pull Request                                                       | Subject                     |
| :------ | :--------- | :----------------------------------------------------------------- | :-------------------------- |
| 0.0.1   | 2024-02-19 | [GitHub](https://github.com/propeldata/airbyte-destination/pull/1) | Initial Propel destination. |
