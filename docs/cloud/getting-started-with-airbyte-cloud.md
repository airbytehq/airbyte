# Getting Started with Airbyte Cloud

This page guides you through setting up your Airbyte Cloud account, setting up a source, destination, and connection, verifying the sync, and allowlisting an IP address.

## Set up your Airbyte Cloud account

To use Airbyte Cloud:

1. If you haven't already, [sign up for Airbyte Cloud](https://cloud.airbyte.com/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=SetupGuide) using your email address, Google login, or GitHub login.

   Airbyte Cloud offers a 14-day free trial that begins after your first successful sync. For more information, see [Pricing](https://airbyte.com/pricing).

   :::note
   If you are invited to a workspace, you currently cannot use your Google login to create a new Airbyte account.
   :::

2. If you signed up using your email address, Airbyte will send you an email with a verification link. On clicking the link, you'll be taken to your new workspace.

   :::info
   A workspace lets you collaborate with team members and share resources across your team under a shared billing account.
   :::

## Set up a source

:::info
A source is an API, file, database, or data warehouse that you want to ingest data from.
:::

To set up a source:

1. On the Airbyte Cloud dashboard, click **Sources**.
2. On the Set up the source page, select the source you want to set up from the **Source catalog**. Airbyte currently offers more than 200 source connectors in Cloud to choose from. Once you've selected the source, a Setup Guide will lead you through the authentication and setup of the source.

3. Click **Set up source**.

## Set up a destination

:::info
A destination is a data warehouse, data lake, database, or an analytics tool where you want to load your extracted data.
:::

To set up a destination:

1. On the Airbyte Cloud dashboard, click **Destinations**.
2. On the Set up the Destination page, select the destination you want to set up from the **Destination catalog**. Airbyte currently offers more than 38 destination connectors in Cloud to choose from. Once you've selected the destination, a Setup Guide will lead you through the authentication and setup of the source.
3. Click **Set up destination**.

## Set up a connection

:::info
A connection is an automated data pipeline that replicates data from a source to a destination.
:::

Setting up a connection involves configuring the following parameters:

| Replication Setting                                                                                                                                | Description                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| [Destination Namespace](../understanding-airbyte/namespaces.md) and stream prefix                                                                                                   | Where should the replicated data be written to?                                                            |
| Replication Frequency                                                                                                                    | How often should the data sync?                                                                         |
| [Data Residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-data-residency#choose-the-data-residency-for-a-connection) | Where should the data be processed?                                                                     |
| [Schema Propagation](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-schema-changes) | Should schema drift be automated?                                                                      |

After configuring the connection settings, you will then define specifically what data will be synced.

:::info
A connection's schema consists of one or many streams. Each stream is most commonly associated with a database table or an API endpoint. Within a stream, there can be one or many fields or columns.
:::

| Catalog Selection                                                                                                                     | Description                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Stream Selection                                     | Which streams should be replicated from the source to the destination?                       |
| Column Selection                                     | Which fields should be included in the sync?                       |
| [Sync Mode](../understanding-airbyte/connections/README.md)                                                                                                                                | How should the streams be replicated (read and written)?                                                |

To set up a connection:

:::tip

Set your [default data residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-data-residency#choose-your-default-data-residency) before creating a new connection to ensure your data is processed in the correct region.

:::

1. On the Airbyte Cloud dashboard, click **Connections** and then click **+ New connection**.
2. Select a source: 

   - To use a data source you've already set up with Airbyte, select from the list of existing sources. Click the source to use it.
   - To set up a new source, select **Set up a new source** and fill out the fields relevant to your source using the Setup Guide.

3. Select a destination:

   - To use a data source you've already set up with Airbyte, select from the list of existing destinations. Click the destination to use it.
   - To set up a new destination, select **Set up a new destination** and fill out the fields relevant to your destination using the Setup Guide.

   Airbyte will scan the schema of the source, and then display the **Connection Configuration** page.

4. From the **Replication frequency** dropdown, select how often you want the data to sync from the source to the destination. The default replication frequency is **Every 24 hours**. You can also set up [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html).

   Reach out to [Sales](https://airbyte.com/company/talk-to-sales) if you require replication more frequently than once per hour. 

5. From the **Destination Namespace** dropdown, select the format in which you want to store the data in the destination. Note: The default configuration is **Destination default**.

| Destination Namepsace | Description                |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Destination default | All streams will be replicated to the single default namespace defined by the Destination. For more details, see<a href="/understanding-airbyte/namespaces#--destination-connector-settings"> ​​Destination Connector Settings</a> |
| Mirror source structure | Some sources (for example, databases) provide namespace information for a stream. If a source provides namespace information, the destination will mirror the same namespace when this configuration is set. For sources or streams where the source namespace is not known, the behavior will default to the "Destination default" option.  |
| Custom format | All streams will be replicated to a single user-defined namespace. See<a href="/understanding-airbyte/namespaces#--custom-format"> Custom format</a> for more details | 

:::tip
To ensure your data is synced correctly, see our examples of how to use the [Destination Namespace](../understanding-airbyte/namespaces.md#examples)
:::

6. (Optional) In the **Destination Stream Prefix (Optional)** field, add a prefix to stream names. For example, adding a prefix `airbyte_` renames the stream `projects` to `airbyte_projects`. This is helpful if you are sending multiple connections to the same Destination Namespace to ensure connections do not conflict when writing to the destination.

7. Select in the **Detect and propagate schema changes** dropdown whether Airbyte should propagate schema changes. See more details about how we handle [schema changes](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-schema-changes).


8. Activate the streams you want to sync by toggling the **Sync** button on. Use the **Search stream name** search box to find streams quickly. If you want to sync all streams, bulk toggle to enable all streams. 

9. Configure the stream settings:
   1. **Data Destination**: Where the data will land in the destination
   2. **Stream**: The table name in the source
   3. **Sync mode**: How the data will be replicated from the source to the destination. 

      For the source:

      - Select **Full Refresh** to copy the entire dataset each time you sync
      - Select **Incremental** to replicate only the new or modified data

      For the destination:

      - Select **Overwrite** to erase the old data and replace it completely
      - Select **Append** to capture changes to your table
        **Note:** This creates duplicate records
      - Select **Append + Deduped** to mirror your source while keeping records unique (most common)

        **Note:** Some sync modes may not yet be available for the source or destination.

   4. **Cursor field**: Used in **Incremental** sync mode to determine which records to sync. Airbyte pre-selects the cursor field for you (example: updated date). If you have multiple cursor fields, select the one you want.
   5. **Primary key**: Used in **Append + Deduped** sync mode to determine the unique identifier.
   6. Choose which fields or columns to sync. By default, all fields are synced.

10. Click **Set up connection**.
11. Airbyte tests the connectio setup. If the test is successful, Airbyte will save the configuration. If the Replication Frequency uses a preset schedule or CRON, your first sync will immediately begin!

## Verify the sync

Once the first sync has completed, you can verify the sync has completed by checking in Airbyte Cloud and in your destination.

1. On the Airbyte Cloud dashboard, click **Connections**. The list of connections is displayed. Click on the connection you just set up.
2. The **Job History** tab shows each sync run, along with the sync summary of data and rows moved. You can also manually trigger syncs or view detailed logs for each sync here. 
3. Check the data at your destination. If you added a Destination Stream Prefix while setting up the connection, make sure to search for the stream name with the prefix.

## Allowlist IP addresses

Depending on your [data residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-data-residency#choose-your-default-data-residency) location, you may need to allowlist the following IP addresses to enable access to Airbyte:

### United States and Airbyte Default

#### GCP region: us-west3

[comment]: # "IMPORTANT: if changing the list of IP addresses below, you must also update the connector.airbyteCloudIpAddresses LaunchDarkly flag to show the new list so that the correct list is shown in the Airbyte Cloud UI, then reach out to the frontend team and ask them to update the default value in the useAirbyteCloudIps hook!"

- 34.106.109.131
- 34.106.196.165
- 34.106.60.246
- 34.106.229.69
- 34.106.127.139
- 34.106.218.58
- 34.106.115.240
- 34.106.225.141

### European Union

#### AWS region: eu-west-3

- 13.37.4.46
- 13.37.142.60
- 35.181.124.238
