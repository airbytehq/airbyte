# Source Workday

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, provide enhanced capabilities and support for critical enterprise systems. To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte's incubating Workday enterprise source connector currently offers the following features:
* Full Refresh [sync mode](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes). This means that all records for all selected streams will be replaced with every sync.
* Reliable replication at any size with [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).

## Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | No         |
| Replicate Incremental Deletes | No         | 
| SSL connection                | Yes        |
| Namespaces                    | No         | 

## Changelog

<details>
  <summary>Expand to review</summary>

The connector is still incubating, this section only exists to satisfy Airbyte's QA checks.

- 0.1.0

</details>
