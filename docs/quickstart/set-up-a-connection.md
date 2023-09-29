# Set up a Connection

Now that you've learned how to [deploy Airbyte locally](https://docs.airbyte.com/quickstart/deploy-airbyte) and set up your first [source](https://docs.airbyte.com/quickstart/add-a-source) and [destination](https://docs.airbyte.com/quickstart/add-a-destination), it's time to finish the job by creating your very first connection!

On the left side of your main Airbyte dashboard, select **Connections**. You will be prompted to choose which source and destination to use for this connection. As an example, we'll use the **Google Sheets** source and **Local JSON** destination.

## Configure the connection

Once you've chosen your source and destination, you'll be able to configure the connection. You can refer to [this page](https://docs.airbyte.com/cloud/managing-airbyte-cloud/configuring-connections) for more information on each available configuration. For this demo, we'll simply set the **Replication frequency** to a 24 hour interval and leave the other fields at their default values.

![Connection config](../.gitbook/assets/set-up-a-connection/getting-started-connection-config.png)

Next, you can toggle which streams you want to replicate, as well as setting up the desired sync mode for each stream. For more information on the nature of each sync mode supported by Airbyte, see [this page](https://docs.airbyte.com/understanding-airbyte/connections/#sync-modes).

Our test data consists of a single stream cleverly named `Test Data`, which we've enabled and set to `Full Refresh - Overwrite` sync mode.

![Stream config](../.gitbook/assets/set-up-a-connection/getting-started-connection-streams.png)

Click **Set up connection** to complete your first connection. Your first sync is about to begin!

## Connector Dashboard

Once you've finished setting up the connection, you will be automatically redirected to a dashboard containing all the tools you need to keep track of your connection.

![Connection dashboard](../.gitbook/assets/set-up-a-connection/getting-started-connection-success.png)

Here's a basic overview of the tabs and their use:

1. The **Status** tab shows you an overview of your connector's sync schedule and health.
2. The **Job History** tab allows you to check the logs for each sync. If you encounter any errors or unexpected behaviors during a sync, checking the logs is always a good first step to finding the cause and solution.
3. The **Replication** tab allows you to modify the configurations you chose during the connection setup.
4. The **Settings** tab contains additional settings, and the option to delete the connection if you no longer wish to use it.

### Check the data from your first sync

If you followed along and created your own connection using a `Local JSON` destination, you can use this command to check the file's contents to make sure the replication worked as intended (be sure to replace YOUR_PATH with the path you chose in your destination setup, and YOUR_STREAM_NAME with the name of an actual stream you replicated):

```bash
cat /tmp/airbyte_local/YOUR_PATH/_airbyte_raw_YOUR_STREAM_NAME.jsonl
```

You should see a list of JSON objects, each containing a unique `airbyte_ab_id`, an `emitted_at` timestamp, and `airbyte_data` containing the extracted record.

:::tip 
If you are using Airbyte on Windows with WSL2 and Docker, refer to [this guide](https://docs.airbyte.com/operator-guides/locating-files-local-destination) to locate the replicated folder and file.
:::

## What's next?

Congratulations on successfully setting up your first connection using Airbyte Open Source! We hope that this will be just the first step on your journey with us. We support a large, ever-growing [catalog of sources and destinations](https://docs.airbyte.com/integrations/), and you can even [contribute your own](https://docs.airbyte.com/connector-development/).

If you have any questions at all, please reach out to us on [Slack](https://slack.airbyte.io/). If you would like to see a missing feature or connector added, please create an issue on our [Github](https://github.com/airbytehq/airbyte). Our community's participation is invaluable in helping us grow and improve every day, and we always welcome your feedback.

Thank you, and we hope you enjoy using Airbyte!
