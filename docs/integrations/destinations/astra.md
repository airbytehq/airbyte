# Astra DB Destination

This page contains the setup guide and reference information for the destination-astra connector.

Use this destination to load records into [Astra DB](https://www.datastax.com/products/datastax-astra) as vector documents. For each record, the connector concatenates the text fields you select, splits the text into chunks, generates an embedding for each chunk with the embedding service you configure, and writes each chunk as a document in a single Astra DB collection through the [Data API](https://docs.datastax.com/en/astra-db-serverless/api-reference/overview.html).

## Prerequisites

- A Serverless (Vector) database in Astra DB, and its API endpoint. The endpoint looks like `https://<database-id>-<region>.apps.astra.datastax.com`.
- An Astra DB [application token](https://docs.datastax.com/en/astra-db-serverless/administration/manage-application-tokens.html) that can create collections and read and write data in the target keyspace. A token generated from the database's **Overview** tab gets a Database Administrator role scoped to that database, which is sufficient.
- A keyspace in that database. New Serverless (Vector) databases include `default_keyspace`.
- A name for the collection to write to. The connector creates the collection if it doesn't exist.
- An API key for the embedding service you want to use, unless you pick the **Fake** embedder. The connector supports OpenAI, Azure OpenAI, Cohere, and any OpenAI-compatible embedding service.

## Set up an Astra DB database

If you don't already have a Serverless (Vector) database, create one:

1. Create an Astra account at [astra.datastax.com/signup](https://astra.datastax.com/signup).
2. In the Astra Portal, select **Databases**, then click **Create Database**.
3. Select the **Serverless (Vector)** deployment type.
4. Enter a name in the **Database name** field. You can't change the name later. Names must start and end with an alphanumeric character, and can contain the following special characters: `& + - _ ( ) < > . , @`.
5. Select your preferred provider and region. The Free plan offers a limited set of regions. Regions with a lock icon require the Pay As You Go plan.
6. Click **Create Database**. The database starts in `Pending` status, moves to `Initializing`, and you get a notification when it's ready.

## Get the endpoint and token

1. Open the **Overview** tab for your database in the Astra Portal.
2. Under **Database Details**, copy the endpoint and enter it in Airbyte as the **Astra DB Endpoint**.
3. Click **Generate Token**, then copy the token and enter it in Airbyte as the **Astra DB Application Token**. Astra shows the token only once, so store it somewhere safe.
4. Enter the keyspace you want to write to as the **Astra DB Keyspace**, and the collection name as the **Astra DB collection**. To create a keyspace or inspect existing ones, use the **Data Explorer** tab.

## Choose an embedding service

The embedding service determines the vector dimension of your documents. Astra fixes a collection's dimension when the collection is created, so if you change the embedding model or dimension later, write to a new collection. Astra supports vectors of up to 4,096 dimensions.

If you select **OpenAI-compatible**, you must supply the dimension of the model yourself, along with the base URL of the service. Airbyte can't detect it from the service.

The **Fake** embedder generates random vectors. Use it to test the pipeline end to end without paying for embeddings. Don't use it in production, because random vectors make search results meaningless.

## How the connector stores data

Every stream you sync writes into the single collection you configure. The connector creates that collection with the cosine similarity metric and the dimension of your embedding model.

Each document corresponds to one chunk of one record and contains:

- `_id`: a generated UUID.
- `$vector`: the embedding of the chunk.
- `text`: the chunk's text. The connector omits this field if you enable **Do not store raw text**.
- `_ab_stream`: the stream the chunk came from, including its namespace.
- `_ab_record_id`: the primary key of the source record. The connector uses this field to delete outdated chunks in deduplicating sync modes.
- One field for each of the metadata fields you configure.

Because all streams share one collection, filter on `_ab_stream` when you query documents from a specific stream.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

Sync modes behave as follows:

- **Overwrite** deletes only the documents whose `_ab_stream` matches the stream being synced, then writes the new documents. Documents from other streams in the same collection are untouched.
- **Append** adds documents without deleting anything. Syncing the same record again creates duplicate documents.
- **Deduped** modes delete the existing documents for each incoming record's primary key before writing that record's new chunks, so the stream needs a primary key.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). A namespace doesn't create a separate Astra keyspace or collection. It becomes part of the `_ab_stream` value on each document.

## Limitations

Keep the following [Astra DB limits](https://docs.datastax.com/en/astra-db-serverless/api-reference/dataapi-limits.html) in mind when you plan a sync:

- A collection's vector dimension is fixed when the collection is created. To switch to an embedding model with a different dimension, configure a different collection.
- A collection can hold no more than 64 distinct fields across all of its documents. Every metadata field you configure, on every stream that shares the collection, counts toward that limit.
- A database supports approximately 10 collections.
- Indexed string values are limited to 8,000 bytes. The connector creates collections with default indexing, which indexes every field, including `text`. If inserts fail because a chunk is too large, reduce the chunk size.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                   |
|:--------| :--------- | :----------- |:----------------------------------------------------------|
| 0.1.45 | 2026-08-13 | [84359](https://github.com/airbytehq/airbyte/pull/84359) | Update the CDK to remediate CVE-2025-68664 in the langchain dependency |
| 0.1.44 | 2025-03-29 | [56606](https://github.com/airbytehq/airbyte/pull/56606) | Update dependencies |
| 0.1.43 | 2025-03-22 | [56098](https://github.com/airbytehq/airbyte/pull/56098) | Update dependencies |
| 0.1.42 | 2025-03-08 | [55394](https://github.com/airbytehq/airbyte/pull/55394) | Update dependencies |
| 0.1.41 | 2025-03-01 | [54871](https://github.com/airbytehq/airbyte/pull/54871) | Update dependencies |
| 0.1.40 | 2025-02-22 | [54244](https://github.com/airbytehq/airbyte/pull/54244) | Update dependencies |
| 0.1.39 | 2025-02-15 | [53883](https://github.com/airbytehq/airbyte/pull/53883) | Update dependencies |
| 0.1.38 | 2025-02-08 | [53388](https://github.com/airbytehq/airbyte/pull/53388) | Update dependencies |
| 0.1.37 | 2025-02-01 | [52943](https://github.com/airbytehq/airbyte/pull/52943) | Update dependencies |
| 0.1.36 | 2025-01-25 | [52179](https://github.com/airbytehq/airbyte/pull/52179) | Update dependencies |
| 0.1.35 | 2025-01-11 | [51295](https://github.com/airbytehq/airbyte/pull/51295) | Update dependencies |
| 0.1.34 | 2025-01-04 | [50910](https://github.com/airbytehq/airbyte/pull/50910) | Update dependencies |
| 0.1.33 | 2024-12-28 | [50446](https://github.com/airbytehq/airbyte/pull/50446) | Update dependencies |
| 0.1.32 | 2024-12-21 | [50213](https://github.com/airbytehq/airbyte/pull/50213) | Update dependencies |
| 0.1.31 | 2024-12-14 | [49288](https://github.com/airbytehq/airbyte/pull/49288) | Update dependencies |
| 0.1.30 | 2024-11-25 | [48674](https://github.com/airbytehq/airbyte/pull/48674) | Update dependencies |
| 0.1.29 | 2024-10-29 | [47105](https://github.com/airbytehq/airbyte/pull/47105) | Update dependencies |
| 0.1.28 | 2024-10-12 | [46857](https://github.com/airbytehq/airbyte/pull/46857) | Update dependencies |
| 0.1.27 | 2024-10-05 | [46402](https://github.com/airbytehq/airbyte/pull/46402) | Update dependencies |
| 0.1.26 | 2024-09-28 | [46179](https://github.com/airbytehq/airbyte/pull/46179) | Update dependencies |
| 0.1.25 | 2024-09-21 | [45829](https://github.com/airbytehq/airbyte/pull/45829) | Update dependencies |
| 0.1.24 | 2024-09-14 | [45498](https://github.com/airbytehq/airbyte/pull/45498) | Update dependencies |
| 0.1.23 | 2024-09-07 | [45330](https://github.com/airbytehq/airbyte/pull/45330) | Update dependencies |
| 0.1.22 | 2024-08-31 | [44983](https://github.com/airbytehq/airbyte/pull/44983) | Update dependencies |
| 0.1.21 | 2024-08-24 | [44700](https://github.com/airbytehq/airbyte/pull/44700) | Update dependencies |
| 0.1.20 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.19 | 2024-08-17 | [44319](https://github.com/airbytehq/airbyte/pull/44319) | Update dependencies |
| 0.1.18 | 2024-08-12 | [43811](https://github.com/airbytehq/airbyte/pull/43811) | Update dependencies |
| 0.1.17 | 2024-08-10 | [43598](https://github.com/airbytehq/airbyte/pull/43598) | Update dependencies |
| 0.1.16 | 2024-08-03 | [43075](https://github.com/airbytehq/airbyte/pull/43075) | Update dependencies |
| 0.1.15 | 2024-07-27 | [42805](https://github.com/airbytehq/airbyte/pull/42805) | Update dependencies |
| 0.1.14 | 2024-07-20 | [42251](https://github.com/airbytehq/airbyte/pull/42251) | Update dependencies |
| 0.1.13 | 2024-07-13 | [41698](https://github.com/airbytehq/airbyte/pull/41698) | Update dependencies |
| 0.1.12 | 2024-07-10 | [41451](https://github.com/airbytehq/airbyte/pull/41451) | Update dependencies |
| 0.1.11 | 2024-07-09 | [41095](https://github.com/airbytehq/airbyte/pull/41095) | Update dependencies |
| 0.1.10 | 2024-07-06 | [40779](https://github.com/airbytehq/airbyte/pull/40779) | Update dependencies |
| 0.1.9 | 2024-06-29 | [40626](https://github.com/airbytehq/airbyte/pull/40626) | Update dependencies |
| 0.1.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.7 | 2024-06-25 | [40467](https://github.com/airbytehq/airbyte/pull/40467) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40162](https://github.com/airbytehq/airbyte/pull/40162) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39198](https://github.com/airbytehq/airbyte/pull/39198) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4   | 2024-05-16 | [38181](https://github.com/airbytehq/airbyte/pull/38181) | Add explicit projection when reading from Astra DB        |
| 0.1.3   | 2024-04-19 | [37405](https://github.com/airbytehq/airbyte/pull/37405) | Add "airbyte" user-agent in the HTTP requests to Astra DB |
| 0.1.2   | 2024-04-15 |              | Moved to Poetry; Updated CDK & pytest versions            |
| 0.1.1   | 2024-01-26 |              | DS Branding Update                                        |
| 0.1.0   | 2024-01-08 |              | Initial Release                                           |

</details>
