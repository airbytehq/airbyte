---
products: cloud
---

# Setting data residency

In Airbyte Cloud, you can set the default data residency for your workspace and also set the the data residency for individual connections, which can help you comply with data localization requirements.

## Choose your workspace default data residency

Setting a default data residency allows you to choose where your data is processed. Set the default data residency **before** creating a new source or connection so that subsequent workflows that rely on the default data residency, such as fetching the schema or testing the source or destination, can process data in the correct region.

:::note

While the data is processed in a data plane of the chosen residency, the cursor and primary key data is stored in the US control plane. If you have data that cannot be stored in the US, do not use it as a cursor or primary key.

:::

When you set the default data residency, it applies your preference to new connections only. If you do not adjust the default data residency, the [Airbyte Default](configuring-connections.md) region is used (United States). If you want to change the data residency for an individual connection, you can do so in its [connection settings](configuring-connections.md).

To choose your default data residency, click **Settings** in the Airbyte UI. Navigate to **Workspace** > **Data Residency**. Use the dropdown to choose the location for your default data residency and save your changes.

:::info

Depending on your network configuration, you may need to add [IP addresses](/operating-airbyte/security.md#network-security-1) to your allowlist.

:::

## Choose the data residency for a connection

:::info
As of November 2024, the option to enable a custom data residency for a connection has been deprecated from Airbyte Cloud.
:::

You can additionally choose the data residency for your connection in the connection settings. You can choose the data residency when creating a new connection, or you can set the default data residency for your workspace so that it applies for any new connections moving forward.

To choose a custom data residency for your connection, click **Connections** in the Airbyte UI and then select the connection that you want to configure. Navigate to the **Settings** tab, open the **Advanced Settings**, and select the **Data residency** for the connection.

:::note

Changes to data residency will not affect any sync in progress.

:::

## Connector Builder data residency

The Connector Builder currently processes all data through US data planes, regardless of your workspace's default data residency settings. This limitation applies to the development and testing of connectors within the builder interface.

If your use case requires strict data residency compliance outside the US, you can still publish a custom connector from the builder which will respect your workspace's data residency settings during syncs. However, you will be unable to verify the connector's behavior within the builder itself.
