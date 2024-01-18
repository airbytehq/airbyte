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

When you set the default data residency, it applies your preference to new connections only. If you do not adjust the default data residency, the [Airbyte Default](configuring-connections.md) region is used (United States).  If you want to change the data residency for an individual connection, you can do so in its [connection settings](configuring-connections.md).

To choose your default data residency:

1. In the Airbyte UI, click **Settings**.

2. Click **Data Residency**.

3. Click the dropdown and choose the location for your default data residency.

4. Click **Save changes**. 

:::info 

Depending on your network configuration, you may need to add [IP addresses](/operating-airbyte/security.md#network-security-1) to your allowlist.   

:::

## Choose the data residency for a connection
You can additionally choose the data residency for your connection in the connection settings. You can choose the data residency when creating a new connection, or you can set the default data residency for your workspace so that it applies for any new connections moving forward.

To choose a custom data residency for your connection: 

1. In the Airbyte UI, click **Connections** and then click the connection that you want to change. 

2. Click the **Settings** tab. 

3. Click the **Data residency** dropdown and choose the location for your default data residency.

4. Click **Save changes**

:::note 

Changes to data residency will not affect any sync in progress. 

:::
