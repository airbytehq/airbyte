# Getting Started with Airbyte Cloud

This page guides you through setting up your Airbyte Cloud account, setting up a source, destination, and connection, verifying the sync, and allowlisting an IP address.

## Set up your Airbyte Cloud account

To use Airbyte Cloud:

1. If you haven't already, [sign up for Airbyte Cloud](https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=SetupGuide) using your email address, Google login, or GitHub login.

   Airbyte Cloud offers a 14-day free trial. For more information, see [Pricing](https://airbyte.com/pricing).

   :::note
   If you are invited to a workspace, you cannot use your Google login to create a new Airbyte account.
   :::

2. If you signed up using your email address, Airbyte will send you an email with a verification link. On clicking the link, you'll be taken to your new workspace.

   :::info
   A workspace lets you collaborate with team members and share resources across your team under a shared billing account.
   :::

You will be greeted with an onboarding tutorial to help you set up your first connection. If you haven’t set up a connection on Airbyte Cloud before, we highly recommend following the tutorial. If you are familiar with the connection setup process, click **Skip Onboarding** and follow this guide to set up your next connection.

## Set up a source

:::info
A source is an API, file, database, or data warehouse that you want to ingest data from.
:::

To set up a source:

1. On the Airbyte Cloud dashboard, click **Sources** and then click **+ New source**.
2. On the Set up the source page, select the source you want to set up from the **Source type** dropdown.

   The fields relevant to your source are displayed. The Setup Guide provides information to help you fill out the fields for your selected source.

3. Click **Set up source**.

## Set up a destination

:::info
A destination is a data warehouse, data lake, database, or an analytics tool where you want to load your extracted data.
:::

To set up a destination:

1. On the Airbyte Cloud dashboard, click **Destinations** and then click **+ New destination**.
2. On the Set up the destination page, select the destination you want to set up from the **Destination type** dropdown.

   The fields relevant to your destination are displayed. The Setup Guide provides information to help you fill out the fields for your selected destination.

3. Click **Set up destination**.

## Set up a connection

:::info
A connection is an automated data pipeline that replicates data from a source to a destination.
:::

Setting up a connection involves configuring the following parameters:

| Parameter                              | Description                                                                                                                                                                                                                                                           |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Replication frequency                  | How often should the data sync?                                                                                                                                                                                                                                       |
| Data residency                         | Where should the data be processed? To choose the preferred data processing location for all of your connections, set your default [data residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud#choose-your-default-data-residency). |
| Destination Namespace and stream names | Where should the replicated data be written?                                                                                                                                                                                                                          |
| Catalog selection                      | Which streams and fields should be replicated from the source to the destination?                                                                                                                                                                                     |
| Sync mode                              | How should the streams be replicated (read and written)?                                                                                                                                                                                                              |
| Optional transformations               | How should Airbyte protocol messages (raw JSON blob) data be converted into other data representations?                                                                                                                                                               |

For more information, see [Connections and Sync Modes](../understanding-airbyte/connections/README.md) and [Namespaces](../understanding-airbyte/namespaces.md)

If you need to use [cron scheduling](http://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html):
1. In the **Replication Frequency** dropdown, click **Cron**. 
2. Enter a cron expression and choose a time zone to create a sync schedule.

:::note

* Only one sync per connection can run at a time. 
* If cron schedules a sync to run before the last one finishes, the scheduled sync will start after the last sync completes.
* Cloud does not allow schedules that sync more than once per hour. 

:::

To set up a connection:

1. On the Airbyte Cloud dashboard, click **Connections** and then click **+ New connection**.
2. On the New connection page, select a source:

   - To use an existing source, select your desired source from the **Source** dropdown. Click **Use existing source**.

   - To set up a new source, select the source you want to set up from the **Source type** dropdown. The fields relevant to your source are displayed. The Setup Guide provides information to help you fill out the fields for your selected source. Click **Set up source**.

3. Select a destination:

   - To use an existing destination, select your desired destination from the **Destination** dropdown. Click **Use existing destination**.
   - To set up a new destination, select the destination you want to set up from the **Destination type** dropdown. The fields relevant to your destination are displayed. The Setup Guide provides information to help you fill out the fields for your selected destination. Click **Set up destination**.

   The Set up the connection page is displayed.

4. From the **Replication frequency** dropdown, select how often you want the data to sync from the source to the destination.

   **Note:** The default replication frequency is **Every 24 hours**.

5. From the **Destination Namespace** dropdown, select the format in which you want to store the data in the destination:

   **Note:** The default configuration is **Mirror source structure**.

   <table>
   <tr>
   <td><strong>Configuration</strong>
   </td>
   <td><strong>Description</strong>
   </td>
   </tr>
   <tr>
   <td>Mirror source structure
   </td>
   <td>Some sources (for example, databases) provide namespace information for a stream. If a source provides the namespace information, the destination will reproduce the same namespace when this configuration is set. For sources or streams where the source namespace is not known, the behavior will default to the "Destination default" option
   </td>
   </tr>
   <tr>
   <td>Destination default
   </td>
   <td>All streams will be replicated and stored in the default namespace defined on the Destination Settings page. For more information, see<a href="https://docs.airbyte.com/understanding-airbyte/namespaces#destination-connector-settings"> ​​Destination Connector Settings</a>
   </td>
   </tr>
   <tr>
   <td>Custom format
   </td>
   <td>All streams will be replicated and stored in a custom format. See<a href="https://docs.airbyte.com/understanding-airbyte/namespaces#custom-format"> Custom format</a> for more details
   </td>
   </tr>
   </table>

:::tip
To better understand the destination namespace configurations, see [Destination Namespace example](../understanding-airbyte/namespaces.md#examples)
:::

6. (Optional) In the **Destination Stream Prefix (Optional)** field, add a prefix to stream names (for example, adding a prefix `airbyte_` renames `projects` to `airbyte_projects`).
7. (Optional) Click **Refresh schema** if you had previously triggered a sync with a subset of tables in the stream and now want to see all the tables in the stream.
8. Activate the streams you want to sync:
   - (Optional) If your source has multiple tables, type the name of the stream you want to enable in the **Search stream name** search box.
   - (Optional) To configure the sync settings for multiple streams, select the checkbox next to the desired streams, configure the settings in the purple box, and click **Apply**.
9. Configure the sync settings:

   1. Toggle the **Sync** button to enable sync for the stream.
   2. **Source:**
      1. **Namespace**: The database schema of your source tables (auto-populated for your source)
      2. **Stream name**: The table name in the source (auto-populated for your source)
   3. **Sync mode**: Select how you want the data to be replicated from the source to the destination:

      For the source:

      - Select **Full Refresh** to copy the entire dataset each time you sync
      - Select **Incremental** to replicate only the new or modified data

      For the destination:

      - Select **Overwrite** to erase the old data and replace it completely
      - Select **Append** to capture changes to your table
        **Note:** This creates duplicate records
      - Select **Deduped + history** to mirror your source while keeping records unique

        **Note:** Some sync modes may not yet be available for your source or destination

   4. **Cursor field**: Used in **Incremental** sync mode to determine which records to sync. Airbyte pre-selects the cursor field for you (example: updated date). If you have multiple cursor fields, select the one you want.
   5. **Primary key**: Used in **Deduped + history** sync mode to determine the unique identifier.
   6. **Destination**:
      - **Namespace:** The database schema of your destination tables.
      - **Stream name:** The final table name in destination.

10. Click **Set up connection**.
11. Airbyte tests the connection. If the sync is successful, the Connection page is displayed.

## Verify the connection

Verify the sync by checking the logs:

1. On the Airbyte Cloud dashboard, click **Connections**. The list of connections is displayed. Click on the connection you just set up.
2. The Sync History is displayed. Click on the first log in the sync history.
3. Check the data at your destination. If you added a Destination Stream Prefix while setting up the connection, make sure to search for the stream name with the prefix.

## Allowlist IP address
Depending on your [data residency](https://docs.airbyte.com/cloud/managing-airbyte-cloud#choose-your-default-data-residency) location, you may need to allowlist the following IP addresses to enable access to Airbyte:

### United States and Airbyte Default
#### GCP region: us-west3
* 34.106.109.131
* 34.106.196.165
* 34.106.60.246

### European Union
#### GCP region: us-west3
* 34.106.109.131
* 34.106.196.165
* 34.106.60.246

#### AWS region: eu-west-3
* 13.37.4.46
* 13.37.142.60
* 35.181.124.238
