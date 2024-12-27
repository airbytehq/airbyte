# deepset Cloud

## General

The Airbyte deepset destination connector allows you to stream data into deepset Cloud from [any Airbyte Source](https://airbyte.io/connectors?connector-type=Sources) emitting records that match the Document File Type.

deepset Cloud is a **[SaaS platform for building LLM applications](https://docs.cloud.deepset.ai/docs/getting-started)** and managing them across the whole lifecycle - from early prototyping to large-scale production.

## Getting started

In order to use the deepset destination, you'll first need to log into your account and generate an API key. If you do not already have an account you can **[find out more here](https://www.deepset.ai/deepset-cloud-product)**

To set up the destination connector in Airbyte, you'll need to provide the following properties:

- **Base URL**: The API host URL for the **deepset Cloud environment** where your account resides. That is,
  `https://api.cloud.deepset.ai` or `https://api.us.deepset.ai` for EU or US multi-tenant users respectively, or the custom API
  host URL of your on-prem deployment. Defaults to `https://api.cloud.deepset.ai`.
- **API Key**: A deepset Cloud API key (see above how to generate an API key-token pair)
- **Workspace Name**: The name of the deepset Cloud workspace where the data will be stored.
- **Retry Count**: The number of times to retry syncing a record before marking it as failed. Defaults to 5 times.

As soon as you've connected a source and the **first stream synchronization** has **succeeded**, the
desired records will be available in deepset Cloud [Files Page](https://cloud.deepset.ai/files) as Markdown files.

Visit our [Getting Started](https://docs.cloud.deepset.ai/docs/getting-started) page for more information about

## Connector overview

### Features

| Feature                                                                                                                   | Support|
| :---------------------------------------------------------------------------------------------------------------------- | :------- |
| [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append/)                |   ✅     |
| [Full Refresh - Replace](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)            |   ✅     |
| [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/)             |   ✅     |
| [Incremental - Append + Deduped ](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)|   ✅     |

### Notes

The connector only ever writes data to the workspace but never deletes. If a file already exists in the destination workspace it is overwritten.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------- |
| 0.1.0   | 2025-01-05 | [48875](https://github.com/airbytehq/airbyte/pull/48875) | Initial release                        |

</details>