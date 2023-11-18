# Chroma
This page guides you through the process of setting up the [Chroma](https://docs.trychroma.com/?lang=py) destination connector.



## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |

#### Output Schema

Only one stream will exist to collect data from all source streams. This will be in a [collection](https://docs.trychroma.com/usage-guide#using-collections) in [Chroma](https://docs.trychroma.com/?lang=py) whose name will be defined by the user, and validated and corrected by Airbyte. 

For each record, a UUID string is generated and used as the document id. The embeddings generated as defined will be stored as embeddings. Data in the text fields will be stored as documents and those in the metadata fields will be stored as metadata.

## Getting Started \(Airbyte Open-Source\)


You can connect to a Chroma instance either in client/server mode or in a local persistent mode. For the local persistent mode, the database file will be saved in the path defined in the `path` config parameter. Note that `path` must be an absolute path, prefixed with `/local`.

:::danger

Persistent Client mode is not supported on Kubernetes

:::

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

#### Requirements

To use the Chroma destination, you'll need:
- An account with API access for OpenAI, Cohere (depending on which embedding method you want to use) or neither (if you want to use the [default chroma embedding function](https://docs.trychroma.com/embeddings#default-all-minilm-l6-v2))
- A Chroma db instance (client/server mode or persistent mode)
- Credentials (for cient/server mode)
- Local File path (for Persistent mode)

#### Configure Network Access

Make sure your Chroma database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.


### Setup the Chroma Destination in Airbyte

You should now have all the requirements needed to configure Chroma as a destination in the UI. You'll need the following information to configure the Chroma destination:

- (Required) **Text fields to embed**
- (Optional) **Text splitter** Options around configuring the chunking process provided by the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).
- (Required) **Fields to store as metadata**
- (Required) **Collection** The name of the collection in Chroma db to store your data 
- (Required) Authentication method 
  - For client/server mode
    - **Host** for example localhost
    - **Port** for example 8000
    - **Username** (Optional)
    - **Password** (Optional)
  - For persistent mode
    - **Path** The path to the local database file. Note that `path` must be an absolute path, prefixed with `/local`.
- (Optional) Embedding 
  - **OpenAI API key** if using OpenAI for embedding
  - **Cohere API key** if using Cohere for embedding
  - Embedding **Field name** and **Embedding dimensions** if getting the embeddings from stream records

## Changelog

| Version | Date       | Pull Request                                               | Subject                                    |
| :------ | :--------- | :--------------------------------------------------------- | :----------------------------------------- |
| 0.0.6 | 2023-11-13 | [32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema |
| 0.0.5   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563) | Add field mapping option |
| 0.0.4   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option |
| 0.0.3   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size |
| 0.0.2   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820)     | Update CDK | 
| 0.0.1   | 2023-09-08 | [#30023](https://github.com/airbytehq/airbyte/pull/30023) | 🎉 New Destination: Chroma (Vector Database)    |
