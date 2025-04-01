# Source Netsuite

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for
Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team,
provide enhanced capabilities and support for critical enterprise systems.
To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte’s incubating Netsuite enterprise source connector currently offers Full Refresh and cursosr-based Incremental syncs for streams.

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

## Prequisities

- Dedicated read-only Airbyte user with read-only access to tables needed for replication
- A Netsuite environment using **SuiteAnalytics Connect** and the **Netsuite2.com** data source for integrations
- Airbyte does not support connecting over SSL using custom Certificate Authority (CA)

## Setup Guide

### Requirements

- **Host:** Service hostname
- **Port:** Service port (Typically 1708)
- **Account ID:** Identifies the Netsuite account (not the individual user account)
- **User credentials:** Username and Password for a Netsuite user account to connect with Airbyte
- **Role**: A user role with sufficient access on Netsuite for all tables to be replicated and is assigned to the user account

To find details such as host, port, Account ID and role go on Netsuite home page, scroll down to Settings at the bottom left and click "Set Up SuiteAnalytics Connect".

![Netsuite Setup](https://raw.githubusercontent.com/airbytehq/airbyte/refs/heads/master/docs/enterprise-setup/assets/enterprise-connectors/netsuite-setup.png)

Note: the role controls what is visible and not to the connector. At a minimum the "SuiteAnalytics Connect" permission is required to connect to SuiteAnalytics over JDBC, as described in [Netsuite SuiteAnalytics documentations](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4102771016.html#To-set-up-SuiteAnalytics-Connect-permissions-using-Manage-Roles%3A)






