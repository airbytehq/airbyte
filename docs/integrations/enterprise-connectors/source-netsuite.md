# Source Netsuite

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for
Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team,
provide enhanced capabilities and support for critical enterprise systems.
To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte’s incubating SAP HANA enterprise source connector currently offers Full Refresh and cursosr-based Incremental syncs for streams.

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes          |       |

## Prequisities

- Dedicated read-only Airbyte user with read-only access to tables needed for replication
- A Netsuite environment using **SuiteAnalytics Connect** and the **Netsuite2.com** data source for integrations
