# Teradata

This page guides you through the process of setting up the Teradata source connector.

## Prerequisites

To use the Teradata source connector, you'll need:

- Access to a Teradata Vantage instance

  **Note:** If you need a new instance of Vantage, you can install a free version called Vantage Express in the cloud on [Google Cloud](https://quickstarts.teradata.com/vantage.express.gcp.html), [Azure](https://quickstarts.teradata.com/run-vantage-express-on-microsoft-azure.html), and [AWS](https://quickstarts.teradata.com/run-vantage-express-on-aws.html). You can also run Vantage Express on your local machine using [VMware](https://quickstarts.teradata.com/getting.started.vmware.html), [VirtualBox](https://quickstarts.teradata.com/getting.started.vbox.html), or [UTM](https://quickstarts.teradata.com/getting.started.utm.html).

You'll need the following information to configure the Teradata source:

- **Host** - The host name of the Teradata Vantage instance.
- **Username**
- **Password**
- **Database** - Specify the database (equivalent to schema in some databases i.e. **database_name.table_name** when performing queries).
- **JDBC URL Params** (optional)
- **SSL Connection** (optional)
- **SSL Modes** (optional)

[Refer to this guide for more details](https://downloads.teradata.com/doc/connectivity/jdbc/reference/current/jdbcug_chapter_2.html#BGBHDDGB)

## Supported sync modes

The Teradata source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                                        | Supported?                                                 |
| :--------------------------------------------- | :--------------------------------------------------------- |
| Full Refresh Sync                              | Yes                                                        |
| Incremental Sync                               | Yes                                                        |
| Replicate Incremental Deletes                  | No                                                         |
| Replicate Multiple Streams \(distinct tables\) | Yes                                                        |
| Namespaces                                     | No (separate connection is needed for different databases) |

### Performance considerations

## Getting started

### Requirements

You need a Teradata user which has read permissions on the database

### Setup guide

#### Set up the Teradata Source connector

1. Log into your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Teradata** from the **Source type** dropdown.
4. Enter the **Name** for the Teradata connector.
5. For **Host**, enter the host domain of the Teradata instance
6. For **Database**, enter the database name (equivalent to schema in some other databases).
7. For **User** and **Password**, enter the database username and password.
8. To customize the JDBC connection beyond common options, specify additional supported [JDBC URL parameters](https://downloads.teradata.com/doc/connectivity/jdbc/reference/current/jdbcug_chapter_2.html#BGBHDDGB) as key-value pairs separated by the symbol & in the **JDBC URL Params** field.

   Example: key1=value1&key2=value2&key3=value3

   These parameters will be added at the end of the JDBC URL that the AirByte will use to connect to your Teradata database.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.2.2   | 2024-02-13 | [35219](https://github.com/airbytehq/airbyte/pull/35219) | Adopt CDK 0.20.4            |
| 0.2.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version            |
| 0.2.0   | 2023-12-18 | https://github.com/airbytehq/airbyte/pull/33485          | Remove LEGACY state         |
| 0.1.0   | 2022-03-27 | https://github.com/airbytehq/airbyte/pull/24221          | New Source Teradata Vantage |

</details>