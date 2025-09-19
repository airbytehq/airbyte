---
products: all
---

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Add and manage destinations

A destination is the data warehouse, data lake, database, or other system to which you sync data. Adding a destination is the next step after you create [a source](add-a-source).

## Add a destination connector

Add a new destination connector to Airbyte.

1. In the left navigation, click **Destinations**.

2. Click **New Destination**.

3. Find the destination you want to add. If you're not sure yet, click the **Marketplace** tab, then click **End-to-End Testing (/dev/null)**. This is a test destination to simulate syncs, but it doesn't move your data anywhere. If you're using Airbyte Cloud, **Google Sheets** is easy to authenticate with, making it a great destination to test your first sync.

4. Configure your connector using the form on the left side of your screen. Every connector has different options and settings, but you normally enter things like authentication information and the location where you store your data. Use the documentation panel on the right side of your screen for help populating the form.

5. Click **Set up destination**. Airbyte tests the destination to ensure it can make a connection. Once the test completes, Airbyte takes you to that connector's Connections page, which is empty at this point.

<Arcade id="qeqpYHmsne7855bFou5Z" title="Set up a new source" paddingBottom="calc(50%)" />

## Modify a destination connector

After you set up a destination connector, you can modify it.

1. In the left navigation, click **Destinations**.

2. Find and click the destination connector you want to modify.

3. Configure your connector using the form on the left side of your screen. Every connector has different options and settings, but you normally enter things like authentication information and the location where you store your data. Use the documentation panel on the right side of your screen for help populating the form.

4. Click **Test and save**. Airbyte tests the destination to ensure it can make a connection.

## Delete a destination connector

You can delete a destination you no longer need.

:::danger
Deleting a destination connector also deletes any connections that rely on it. Data that's already in your destination isn't affected. However, reestablishing this connection later requires a full re-sync.
:::

1. In the left navigation, click **Destinations**.

2. Find and click the destination connector you want to modify.

3. Click **Delete this destination**.

4. In the dialog, type the name of the connector, then click **Delete**.

## Reusing destination connectors

Connectors are reusable. In most cases, you only need to set up the connector once, and you can use it in as many connections as you need to.

## Other ways to manage destinations

Airbyte has other options to manage connectors, too.

- [Airbyte API](https://reference.airbyte.com/reference/createdestination#/)
- [Terraform](../../terraform-documentation)

In these cases, you can speed up the process by entering your values into the UI, then clicking the **Copy JSON** button. This copies your configuration as a JSON string that you can paste into your code.
