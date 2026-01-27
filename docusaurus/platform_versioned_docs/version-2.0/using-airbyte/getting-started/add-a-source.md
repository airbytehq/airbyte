---
products: all
---

# Add and manage sources

A source is the database, API, or other system from which you sync data. Adding a source connector is the first step when you want to start syncing data with Airbyte.

## Add a source connector

Add a new source connector to Airbyte.

1. In the left navigation, click **Sources**.

2. Click **New Source**.

3. Find the source you want to add. If you're not sure yet, click the **Marketplace** tab, then click **Sample Data (Faker)**. Faker is a popular test source that generates random data.

4. Configure your connector using the form on the left side of your screen. Every connector has different options and settings, but you normally enter things like authentication information and the location where you store your data. Use the documentation panel on the right side of your screen for help populating the form.

5. Click **Set up source**. Airbyte tests the source to ensure it can make a connection. Once the test completes, Airbyte takes you to the New Connection page, where you can set up a new destination connector, or choose one you previously created.

<Arcade id="MOZ8NhasIpvf6M9Xkpna" title="Set up a new source" paddingBottom="calc(50%)" />

## Modify a source connector

After you set up a source connector, you can modify it.

1. In the left navigation, click **Sources**.

2. Find and click the source connector you want to modify.

3. Configure your connector using the form on the left side of your screen. Every connector has different options and settings, but you normally enter things like authentication information and the location where you store your data. Use the documentation panel on the right side of your screen for help populating the form.

4. Click **Test and save**. Airbyte tests the source to ensure it can make a connection.

## Delete a source connector

You can delete a source you no longer need. 

:::danger
Deleting a source connector also deletes any connections that rely on it. Data that's already in your destination isn't affected. However, reestablishing this connection later requires a full re-sync.
:::

1. In the left navigation, click **Sources**.

2. Find and click the source connector you want to modify.

3. Click **Delete this source**.

4. In the dialog, type the name of the connector, then click **Delete**.

## Reusing source connectors

Connectors are reusable. In most cases, you only need to set up the connector once, and you can use it in as many connections as you need to.

In a few cases, you might need to set up the same source connector multiple times. For example, if you are pulling data from multiple accounts that have unique authentication, you need a separate connector for each account.

## If you don't see the connector you need

If Airbyte doesn't have the connector you need, [you can create your own](../../connector-development/). In most cases, you want to use the Connector Builder, a no-code/low-code development environment in Airbyte's UI.

## Other ways to manage sources

Airbyte has other options to manage connectors, too.

- [Airbyte API](https://reference.airbyte.com/reference/createsource#/)
- [Terraform](../../terraform-documentation)

In these cases, you can speed up the process by entering your values into the UI, then clicking the **Copy JSON** button. This copies your configuration as a JSON string that you can paste into your code.
