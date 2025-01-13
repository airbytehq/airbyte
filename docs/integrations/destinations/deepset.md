# deepset Cloud

deepset Cloud is a SaaS platform for building LLM applications and managing them across the whole lifecycle - from early prototyping to large-scale production. For details, see [deepset Cloud documentation](https://docs.cloud.deepset.ai/docs/getting-started).

## Data Integration with Airbyte

To make it possible to synchronize data to deepset Cloud using Airbyte, we've added an Airbyte deepset destination connector. You can use it to stream data into deepset Cloud from any Airbyte source that emits records matching the document file type. The synchronized data are available in deepset Cloud on the Files page as Markdown files.

_Note_: The deepset destination connector writes data to your deepset Cloud workspace, but does not delete any data from the workspace. If a file with the same name already exists in the destination workspace, it is overwritten.

### Supported Sync Modes

The deepset destination connector supports the following sync modes:

* [Full refresh - append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append/)
* [Full refresh - overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Incremental sync - append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/)
* [Incremental sync - append + deduped ](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Syncing Data to deepset Cloud

To use the deepset destination in Airbyte:

1. Log in to deepset Cloud.

2. Generate the deepset Cloud API key:

    - Click your initials in the top right corner and choose Connections.
    - Scroll down the Connections page to the API Keys section and click _Add new key_. If you need help, see [Generate an API Key](https://docs.cloud.deepset.ai/docs/generate-api-key).

3. Set up the destination connector in Airbyte providing the following details:

    - `Base URL`: This is the URL for the deepset Cloud environment with your account. Possible options are: `https://api.cloud.deepset.ai` (default) for EU users , `https://api.us.deepset.ai` for US users, or custom URL for on-premise deployments.
    - `API key`: Your deepset Cloud API key (generated in step 2 above).
    - `Workspace name`: The name of the deepset Cloud workspace where you want to store the data.
    - `Retry count`: The number of times to retry syncing a record before marking it as failed. Defaults to 5 times.

After you connect a source and the first stream synchronization succeeds, your records are available in deepset Cloud on the Files page as Markdown files.

# Changelog


<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------- |
| 0.1.0   | 2025-01-10 | [48875](https://github.com/airbytehq/airbyte/pull/48875) | Initial release                        |

</details>