# Getting Started with Airbyte Cloud

This page guides you through setting up your Airbyte Cloud account, setting up a source, destination, and connection, verifying the sync, and allowlisting an IP address.

## Set up your Airbyte Cloud account

To use Airbyte Cloud:

1. If you haven't already, [sign up for Airbyte Cloud](https://cloud.airbyte.io/signup?utm_campaign=22Q1_AirbyteCloudSignUpCampaign_Trial&utm_source=Docs&utm_content=SetupGuide). 

    Airbyte Cloud offers a 14-day free trial with $1000 worth of [credits](core-concepts.md#credits), whichever expires first. For more information, see [Pricing](https://airbyte.com/pricing).

2. Airbyte will send you an email with a verification link. On clicking the link, you'll be taken to your new workspace.

    :::info
    A workspace lets you collaborate with team members and share resources across your team under a shared billing account.
    :::

You will be greeted with an onboarding tutorial to help you set up your first connection. If you haven’t set up a connection on Airbyte Cloud before, we highly recommend following the tutorial. If you are familiar with the connection setup process, click **Skip onboarding** and follow this guide to set up your next connection.

## Set up a source

:::info
A source is an API, file, database, or data warehouse that you want to ingest data from.
:::

To set up a source:

1. On the Airbyte Cloud dashboard, click **Sources** in the left navigation bar. 
2. In the top right corner, click **+ new source**. 
3. On the Set up the source page, enter a name for your source.
4. From the Source type dropdown, select the source you want to set up.
5. The fields relevant to your source are displayed. 
Click **Setup Guide** for help with filling in the fields for your selected source.
6. Click **Set up source**. 

## Set up a destination

:::info
A destination is a data warehouse, data lake, database, or an analytics tool where you want to load your extracted data.
:::

To set up a destination:

1. On the Airbyte Cloud dashboard, click **Destinations** in the left navigation bar. 
2. In the top right corner, click **+ new destination**.
3. On the Set up the destination page, enter a name for your destination.
4. From the Destination type dropdown, select the destination you want to set up.
5. The fields relevant to your destination are displayed. 
    Click **Setup Guide** for help with filling in the fields for your selected destination.
6. Click **Set up destination**. 

## Set up a connection

:::info
A connection is an automated data pipeline that replicates data from a source to a destination.
:::

Setting up a connection involves configuring the following parameters:

<table>
  <tr>
   <td><strong>Parameter</strong>
   </td>
   <td><strong>Description</strong>
   </td>
  </tr>
  <tr>
   <td>Sync schedule
   </td>
   <td>When should a data sync be triggered?
   </td>
  </tr>
  <tr>
   <td>Destination Namespace and stream names
   </td>
   <td>Where should the replicated data be written?
   </td>
  </tr>
  <tr>
   <td>Catalog selection
   </td>
   <td>Which streams and fields should be replicated from the source to the destination?
   </td>
  </tr>
  <tr>
   <td>Sync mode
   </td>
   <td>How should the streams be replicated (read and written)?
   </td>
  </tr>
  <tr>
   <td>Optional transformations
   </td>
   <td>How should Airbyte protocol messages (raw JSON blob) data be converted into other data representations?
   </td>
  </tr>
</table>


For more information, see [Connections and Sync Modes](../understanding-airbyte/connections/README.md) and [Namespaces](../understanding-airbyte/namespaces.md)

To set up a connection:

1. On the Airbyte Cloud dashboard, click **Connections** in the left navigation bar. 
2. In the top right corner, click **+ new connection**. 
3. On the New Connection page, select a source:
    - To use an existing source, select your desired source from the Source dropdown. Click **Use existing source**. 

    -  To set up a new source, enter a name for the new source and select the source from the Source type dropdown. The fields relevant to your source are displayed. Click **Setup Guide** for help with filling in the fields for your selected source. Click **Set up source**.

4. Select a destination:
    - To use an existing destination, select your desired destination from the Destination dropdown. Click **Use existing destination**. 
    - To set up a new destination, enter a name for the new destination and select the destination from the Destination type dropdown. The fields relevant to your destination are displayed. Click **Setup Guide** for help with filling in the fields for your selected source. Click **Set up destination**.
	
    The Set up the connection page is displayed.
5. From the **Replication frequency** dropdown, select how often you want the data to sync from the source to the destination. 
        
    **Note:** The default replication frequency is 24 hours.

6. From the **Destination Namespace** dropdown, select the format in which you want the data to stored in the destination:
	
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
    <td>All streams will be replicated and stored in the default namespace defined on the destination settings page. For settings for popular destinations, see<a href="https://docs.airbyte.com/understanding-airbyte/namespaces#destination-connector-settings"> ​​Destination Connector Settings</a>
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

7. (Optional) In the **Destination Stream Prefix (Optional)** field, add a prefix to stream names (for example, adding a prefix `airbyte_` renames `projects` to  `airbyte_projects`).
8. (Optional) Click **Refresh schema** if you had previously triggered a sync with a subset of tables in the stream and now want to see all the tables in the stream.
9. Activate the streams you want to sync:
    - (Optional) If your source has multiple tables, type the name of the stream you want to enable in the **Search box**.
    - (Optional) To configure the sync settings for multiple streams, select the checkbox next to the desired streams, configure the settings in the purple box, and click **Apply**.
10. Configure the sync settings and click **Set up connection**:
    1. Toggle the **Sync** button to enable sync for the stream.
    2. **Source:**
        1. **Namespace**: The database schema of your source tables (auto-populated for your source)
        2. **Stream name**: The table name in the source (auto-populated for your source)
    3. **Sync mode**: Select how you want the data to be replicated from the source to the destination:

        For the source:

        * Select **Full Refresh** to copy the entire dataset each time you sync
        * Select **Incremental only** to replicate only the new or modified data

        For the destination:

        * Select **Overwrite** to erase the old data and replace it completely
        * Select **Append** to capture changes to your table
            
            **Note:** This creates duplicate records
        * Select **Deduped + History** to mirror your source while keeping records unique
                **Note:** Some sync modes may not yet be available for your source or destination

    4. **Cursor field**: Used in incremental sync mode to determine which records to sync. Airbyte pre-selects the Cursor field for you (example: updated date). If you have multiple cursor fields, select the one you want.
    5. **Primary key**: Used in Deduped and History modes to determine the unique identifier.
    6. **Destination**: 
        - **Namespace:** The database schema of your destination tables.
        - **Stream name:** The final table name in destination.
11. If the sync is successful, a success message is displayed.

## Verify the connection

To verify the sync by checking the logs:

1. On the Airbyte Cloud dashboard, click **Connections** in the left navigation bar. The list of connections is displayed. Click on the connection you just set up.
2. The sync history is displayed. Click on the first log in the sync history.
3. Check the data at your destination. If you added a Destination Stream Prefix while setting up the connection, make sure to search for the stream name with the prefix.

## Allowlist IP address

You may need to allowlist `34.106.109.131` to enable access to Airbyte.
