# Manage data residency

In Airbyte Cloud, you can set the default data residency and choose the data residency for individual connections, which can help you comply with data localization requirements.

## Choose your default data residency

Default data residency allows you to choose where your data is processed. Some workflows, such as fetching the schema or testing the source destination, use the default data residency before creating a new connection. To ensure your data is processed in the correct region, set your default data residency before creating a new connection. 

:::note 

While the data is processed in a data plane in the chosen residency, the cursor and primary key data is stored in the US control plane. If you have data that cannot be stored in the US, do not use it as a cursor or primary key.

:::

When you set the default data residency, it applies to new connections only. If you do not set the default data residency, the [Airbyte Default](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud/#united-states-and-airbyte-default) region is used. You can choose a different default residency for each connection in its [connection settings](#choose-the-data-residency-for-a-connection) or when creating a [new connection](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#set-up-a-connection).

To choose your default data residency:

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Settings**.

2. Click **Data Residency**.

3. Click the dropdown and choose the location for your default data residency.

4. Click **Save changes**. 

:::info 

Depending on your network configuration, you may need to add [IP addresses](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud/#allowlist-ip-addresses) to your allowlist.   

:::

## Choose the data residency for a connection
You can choose the data residency for your connection in the connection settings. You can also choose data residency when creating a [new connection](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#set-up-a-connection), or you can set the [default data residency](#choose-your-default-data-residency) for your workspace.

To choose the data residency for your connection: 

1. On the [Airbyte Cloud](http://cloud.airbyte.com) dashboard, click **Connections** and then click the connection that you want to change. 

2. Click the **Settings** tab. 

3. Click the **Data residency** dropdown and choose the location for your default data residency.

4. Click **Save changes**

:::note 

Changes to data residency will not affect any sync in progress. 

:::
