# Pinecone

## Overview

This page guides you through the process of setting up the [Pinecone](https://pinecone.io/) destination connector.

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported.)
* Indexing - store the vectors in a vector database for similarity search

## Prerequisites

To use the Pinecone destination, you'll need:

- An account with API access for OpenAI or Cohere (depending on which embedding method you want to use)
- A Pinecone project with a pre-created index with the correct dimensionality based on your embedding method

You'll need the following information to configure the destination:

- **Embedding service API Key** - The API key for your OpenAI or Cohere account
- **Pinecone API Key** - The API key for your Pinecone account
- **Pinecone Environment** - The name of the Pinecone environment to use
- **Pinecone Index name** - The name of the Pinecone index to load data into

## Features

| Feature                        | Supported?           | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  | Deleting records via CDC is not supported (see issue [#29827](https://github.com/airbytehq/airbyte/issues/29827))  |
| Namespaces                     | No                   |       |

## Data type mapping

All fields specified as metadata fields will be stored in the metadata object of the document and can be used for filtering. The following data types are allowed for metadata fields:
* String
* Number (integer or floating point, gets converted to a 64 bit floating point)
* Booleans (true, false)
* List of String

All other fields are ignored.

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Please note that there's a 40kb limit on the _total_ size of the metadata saved for each entry.

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**. 

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

To get started, use the [Pinecone web UI or API](https://docs.pinecone.io/docs/quickstart) to create a project and an index before running the destination. All streams will be indexed into the same index, the `_ab_stream` metadata field is used to distinguish between streams. Overall, the size of the metadata fields is limited to 30KB per document. 

OpenAI and Fake embeddings produce vectors with 1536 dimensions, and the Cohere embeddings produce vectors with 1024 dimensions. Make sure to configure the index accordingly.

## CHANGELOG

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.0.5   | 2023-09-07 | [#30133](https://github.com/airbytehq/airbyte/pull/30133)     | Refactor internal structure of connector  | 
| 0.0.4   | 2023-09-05 | [#30086](https://github.com/airbytehq/airbyte/pull/30079)     | Switch to GRPC client for improved performance.  | 
| 0.0.3   | 2023-09-01 | [#30079](https://github.com/airbytehq/airbyte/pull/30079)     | Fix bug with potential data loss on append+dedup syncing. 🚨 Streams using append+dedup mode need to be reset after upgrade.  | 
| 0.0.2   | 2023-08-31 | [#29442](https://github.com/airbytehq/airbyte/pull/29946)     | Improve test coverage  | 
| 0.0.1   | 2023-08-29 | [#29539](https://github.com/airbytehq/airbyte/pull/29539)     | Pinecone connector with some embedders  | 
