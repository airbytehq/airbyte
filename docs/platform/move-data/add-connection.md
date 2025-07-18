---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";
import DocCardList from '@theme/DocCardList';

# Add a connection

After you add a [source](../using-airbyte/getting-started/add-a-source) and a [destination](../using-airbyte/getting-started/add-a-destination), add a new connection to start syncing data from your source to your destination.

## ELT and data activation destinations are different

You configure all connections in a similar way. However, the exact process is different for [data activation destinations](elt-data-activation). This page explains how to set up both.

- **ELT databases, warehouses, and lakes**: These destinations are agnostic about schema. You can, for example, create tables with any number of columns and change those column types if you need to. This is typical of data warehouse and data lake types of destinations.

- **Data activation**: Some destinations have strict schemas that your connection must observe. For example, if you're syncing data to Salesforce, your Salesforce records might have specific fields for name, email, company, phone number, revenue, etc. Some of those fields may be optional, some may be required, and all expect data in a certain format. This means you need to map data from your source to your destination to ensure it arrives in the necessary format and structure.

The unique needs of a destination account for why setting up some connections might be different than others.

## Create a connection: databases, warehouses, and lakes

Follow these steps to create a connection to a database, warehouse, lake, or similar type of destination.

1. Click **Connections** in the navigation.

2. Click **New connection**.

3. Click the source you want to add. If you don't have one yet, you can [add one](../using-airbyte/getting-started/add-a-source).

4. Click the destination you want to add. If you don't have one yet, you can [add one](../using-airbyte/getting-started/add-a-destination). Wait a moment while Airbyte fetches the schema of your data.

5. Under **Select sync mode**, select your sync mode. You can either replicate sources, which maintains an up-to-date copy of your source data in the destination, or you can append historical changes, allowing you to track changes to your data over time in your destination. Airbyte automatically selects the most appropriate sync mode for each stream based on this selection. However, you can update specific streams later.

6. In the **Schema** table, configure your schema. 

    1. Choose the specific streams and fields you want to sync.

    2. Choose the sync mode for each stream. To learn more, see [sync modes](/platform/using-airbyte/core-concepts/sync-modes/).

    3. Set primary keys, if applicable.

7. Click **Next**.

8. Under **Configure connection**, finalize the settings for this connection.



## Create a connection: data activation

Follow these steps to create a connection to a data activation destination.
