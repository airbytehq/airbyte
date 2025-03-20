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

## Getting Started \(Airbyte Open Source\)

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                      |
|:--------|:-----------| :-------------------------------------------------------- |:-------------------------------------------------------------|
| 0.0.48 | 2025-03-08 | [55393](https://github.com/airbytehq/airbyte/pull/55393) | Update dependencies |
| 0.0.47 | 2025-03-01 | [54852](https://github.com/airbytehq/airbyte/pull/54852) | Update dependencies |
| 0.0.46 | 2025-02-22 | [54209](https://github.com/airbytehq/airbyte/pull/54209) | Update dependencies |
| 0.0.45 | 2025-02-15 | [53930](https://github.com/airbytehq/airbyte/pull/53930) | Update dependencies |
| 0.0.44 | 2025-02-08 | [53428](https://github.com/airbytehq/airbyte/pull/53428) | Update dependencies |
| 0.0.43 | 2025-02-01 | [52941](https://github.com/airbytehq/airbyte/pull/52941) | Update dependencies |
| 0.0.42 | 2025-01-25 | [52189](https://github.com/airbytehq/airbyte/pull/52189) | Update dependencies |
| 0.0.41 | 2025-01-18 | [51744](https://github.com/airbytehq/airbyte/pull/51744) | Update dependencies |
| 0.0.40 | 2025-01-11 | [51296](https://github.com/airbytehq/airbyte/pull/51296) | Update dependencies |
| 0.0.39 | 2025-01-04 | [50913](https://github.com/airbytehq/airbyte/pull/50913) | Update dependencies |
| 0.0.38 | 2024-12-28 | [50445](https://github.com/airbytehq/airbyte/pull/50445) | Update dependencies |
| 0.0.37 | 2024-12-21 | [50221](https://github.com/airbytehq/airbyte/pull/50221) | Update dependencies |
| 0.0.36 | 2024-12-14 | [48956](https://github.com/airbytehq/airbyte/pull/48956) | Update dependencies |
| 0.0.35 | 2024-11-25 | [48668](https://github.com/airbytehq/airbyte/pull/48668) | Update dependencies |
| 0.0.34 | 2024-11-04 | [48236](https://github.com/airbytehq/airbyte/pull/48236) | Update dependencies |
| 0.0.33 | 2024-10-29 | [47053](https://github.com/airbytehq/airbyte/pull/47053) | Update dependencies |
| 0.0.32 | 2024-10-12 | [46434](https://github.com/airbytehq/airbyte/pull/46434) | Update dependencies |
| 0.0.31 | 2024-09-28 | [46192](https://github.com/airbytehq/airbyte/pull/46192) | Update dependencies |
| 0.0.30 | 2024-09-21 | [45553](https://github.com/airbytehq/airbyte/pull/45553) | Update dependencies |
| 0.0.29 | 2024-09-07 | [45322](https://github.com/airbytehq/airbyte/pull/45322) | Update dependencies |
| 0.0.28 | 2024-08-31 | [45017](https://github.com/airbytehq/airbyte/pull/45017) | Update dependencies |
| 0.0.27 | 2024-08-24 | [44717](https://github.com/airbytehq/airbyte/pull/44717) | Update dependencies |
| 0.0.26 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.0.25 | 2024-08-17 | [44292](https://github.com/airbytehq/airbyte/pull/44292) | Update dependencies |
| 0.0.24 | 2024-08-12 | [43734](https://github.com/airbytehq/airbyte/pull/43734) | Update dependencies |
| 0.0.23 | 2024-08-10 | [43702](https://github.com/airbytehq/airbyte/pull/43702) | Update dependencies |
| 0.0.22 | 2024-08-03 | [43133](https://github.com/airbytehq/airbyte/pull/43133) | Update dependencies |
| 0.0.21 | 2024-07-27 | [42628](https://github.com/airbytehq/airbyte/pull/42628) | Update dependencies |
| 0.0.20 | 2024-07-20 | [42160](https://github.com/airbytehq/airbyte/pull/42160) | Update dependencies |
| 0.0.19 | 2024-07-13 | [41802](https://github.com/airbytehq/airbyte/pull/41802) | Update dependencies |
| 0.0.18 | 2024-07-10 | [41384](https://github.com/airbytehq/airbyte/pull/41384) | Update dependencies |
| 0.0.17 | 2024-07-09 | [41165](https://github.com/airbytehq/airbyte/pull/41165) | Update dependencies |
| 0.0.16 | 2024-07-06 | [40926](https://github.com/airbytehq/airbyte/pull/40926) | Update dependencies |
| 0.0.15 | 2024-06-29 | [40634](https://github.com/airbytehq/airbyte/pull/40634) | Update dependencies |
| 0.0.14 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.0.13 | 2024-06-25 | [40431](https://github.com/airbytehq/airbyte/pull/40431) | Update dependencies |
| 0.0.12 | 2024-06-23 | [40222](https://github.com/airbytehq/airbyte/pull/40222) | Update dependencies |
| 0.0.11 | 2024-06-22 | [40068](https://github.com/airbytehq/airbyte/pull/40068) | Update dependencies |
| 0.0.10  | 2024-04-15 | [#37333](https://github.com/airbytehq/airbyte/pull/37333) | Updated CDK & pytest version to fix security vulnerabilities |
| 0.0.9   | 2023-12-11 | [#33303](https://github.com/airbytehq/airbyte/pull/33303) | Fix bug with embedding special tokens                        |
| 0.0.8   | 2023-12-01 | [#32697](https://github.com/airbytehq/airbyte/pull/32697) | Allow omitting raw text                                      |
| 0.0.7   | 2023-11-16 | [#32608](https://github.com/airbytehq/airbyte/pull/32608) | Support deleting records for CDC sources                     |
| 0.0.6   | 2023-11-13 | [#32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                          |
| 0.0.5   | 2023-10-23 | [#31563](https://github.com/airbytehq/airbyte/pull/31563) | Add field mapping option                                     |
| 0.0.4   | 2023-10-15 | [#31329](https://github.com/airbytehq/airbyte/pull/31329) | Add OpenAI-compatible embedder option                        |
| 0.0.3   | 2023-10-04 | [#31075](https://github.com/airbytehq/airbyte/pull/31075) | Fix OpenAI embedder batch size                               |
| 0.0.2   | 2023-09-29 | [#30820](https://github.com/airbytehq/airbyte/pull/30820) | Update CDK                                                   |
| 0.0.1   | 2023-09-08 | [#30023](https://github.com/airbytehq/airbyte/pull/30023) | 🎉 New Destination: Chroma (Vector Database)                 |

</details>
