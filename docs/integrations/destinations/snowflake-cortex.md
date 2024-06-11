# Snowflake Cortex Destination

## Overview

This page guides you through the process of setting up the [Snowflake](https://www.snowflake.com/en/) as a vector destination.

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported. Coming soon: Hugging Face's `e5-base-v2`).
* Snowflake Connection - where to store the vectors. This configures a vector store using Snowflake tables having the `VECTOR` data type.

## Prerequisites

To use the Snowflake Cortex destination, you'll need:

- An account with API access for OpenAI or Cohere (depending on which embedding method you want to use)
- A Snowflake account with support for vector type columns

You'll need the following information to configure the destination:

- **Embedding service API Key** - The API key for your OpenAI or Cohere account
- **Snowflake Account** - The account name for your Snowflake account
- **Snowflake User** - The user name for your Snowflake account
- **Snowflake Password** - The password for your Snowflake account
- **Snowflake Database** - The database name in Snowflake to load data into
- **Snowflake Warehouse** - The warehouse name in Snowflake to use
- **Snowflake Role** - The role name in Snowflake to use. 


## Features

| Feature                        | Supported?           | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |

## Data type mapping

All fields specified as metadata fields will be stored in the metadata object of the document and can be used for filtering. The following data types are allowed for metadata fields:
* String
* Number (integer or floating point, gets converted to a 64 bit floating point)
* Booleans (true, false)
* List of String

All other fields are ignored.

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Please note that there's a 40kb limit on the _total_ size of the metadata saved for each entry.  Options around configuring the chunking process use the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing/Data Storage 

To get started, sign up for [Snowflake](https://www.snowflake.com/en/). Ensure you have set a database, and a data wareshouse before running the Snowflake Cortex destination. All streams will be indexed/stored into a table with the same name. The table will be created if it doesn't exist. The table will have the following columns: 
- document_id (string) - the unique identifier of the document, creating from appending the primary keys in the stream schema
- chunk_id (string) - the unique identifier of the chunk, created by appending the chunk number to the document_id
- metadata (variant) - the metadata of the document, stored as key-value pairs
- page_content (string) - the text content of the chunk
- embedding (vector) - the embedding of the chunk, stored as a list of floats


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.3 | 2024-06-04 | [38955](https://github.com/airbytehq/airbyte/pull/38955) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.2 | 2024-06-04 | [#39092](https://github.com/airbytehq/airbyte/pull/39092) | Fix writing when multiple chunks exist for a document.
| 0.2.1 | 2024-06-03 | [#38830](https://github.com/airbytehq/airbyte/pull/38830) | Add handling for unexpected/undefined state codes.
| 0.2.0 | 2024-05-30 | [#38337](https://github.com/airbytehq/airbyte/pull/38337) | Fix `merge` behavior when multiple chunks exist for a document. Includes additional refactoring and improvements.
| 0.1.2 | 2024-05-17 | [#38327](https://github.com/airbytehq/airbyte/pull/38327) | Fix chunking related issue.
| 0.1.1 | 2024-05-15 | [#38206](https://github.com/airbytehq/airbyte/pull/38206) | Bug fixes.
| 0.1.0 | 2024-05-13 | [#37333](https://github.com/airbytehq/airbyte/pull/36807) | Add support for Snowflake as a Vector destination.

</details>
